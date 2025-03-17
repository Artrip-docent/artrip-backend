from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Exhibition, Document, Gallery
from .forms import ExhibitionForm, DocumentForm, GalleryForm
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import json
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
import threading
import queue
import pinecone
# --- LangChain 관련 임포트 ---
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler
from pinecone import Pinecone, ServerlessSpec  # Pinecone 클라이언트용
from langchain_pinecone import PineconeVectorStore  # LangChain VectorStore용

# OpenAI Embeddings를 사용하여 벡터스토어 구축 (한 번만 초기화하는 것이 좋습니다)
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

PINECONE_API_KEY = settings.PINECONE_API_KEY  # .env에 설정한 값
PINECONE_ENV = settings.PINECONE_ENV          # 예: "us-east1-aws" 또는 "us-east-1" (Pinecone 대시보드에 맞춰)
INDEX_NAME = settings.PINECONE_INDEX_NAME      # 예: "artwork-index"
# Pinecone 인스턴스 생성
pc = Pinecone(api_key=PINECONE_API_KEY)

# 기존 인덱스 목록 확인 (각 인덱스 객체의 name 속성을 사용)
existing_indexes = [idx.name for idx in pc.list_indexes()]
if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=embeddings.embedding_dim,  # 예: 1536
        metric='cosine',  # 필요에 따라 'euclidean' 또는 'dotproduct' 등 선택
        spec=ServerlessSpec(
            cloud='aws',
            region=PINECONE_ENV
        )
    )
pinecone_index = pc.Index(INDEX_NAME)
index_stats = pinecone_index.describe_index_stats()
print(f"📊 현재 Pinecone 인덱스 상태: {index_stats}")
vector_ids = pinecone_index.describe_index_stats().get('namespaces', {}).get('', {}).get('vector_count', 0)
print(f"📊현재 Pinecone에 저장된 벡터 개수: {vector_ids}")
# Swagger 요청 및 응답 정의
message_param = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, description="User message"),
        "exhibition_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Exhibition ID (optional)"),
    },
    required=["message"],  # exhibition_id는 선택 사항이면 required에 넣지 않음
)

response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "response": openapi.Schema(type=openapi.TYPE_STRING, description="AI response")
    },
)

@swagger_auto_schema(
    method="post",
    request_body=message_param,
    responses={200: response_schema},
    operation_description="GPT-4o-mini와 대화하며 SSE로 응답을 스트리밍합니다.",
)
@api_view(["POST"])
@csrf_exempt
def chat_view(request):
    """
    작품 도슨트 역할을 수행하는 AI 챗봇.
    요청 JSON에 'message'와 (선택적으로) 'exhibition_id'를 포함하여,
    exhibition_id가 있으면 해당 전시회의 문서를 기반으로, 없으면 GPT 응답만 반환합니다.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        exhibition_id = data.get("exhibition_id")  # 전시회 ID

        if not user_message:
            return StreamingHttpResponse(
                "data: {\"error\": \"Message cannot be empty\"}\n\n",
                content_type="text/event-stream",
                status=400
            )

        def event_stream(user_message):
            token_queue = queue.Queue()

            # 콜백 핸들러: 토큰이 생성될 때마다 token_queue로 전달
            class SSECallbackHandler(BaseCallbackHandler):
                def on_llm_new_token(self, token: str, **kwargs) -> None:
                    token_queue.put(token)

            callback_handler = SSECallbackHandler()
            callback_manager = CallbackManager([callback_handler])

            # 공통 프롬프트 템플릿
            prompt_template = PromptTemplate(
                template=(
                    "당신은 작품 도슨트입니다. 모든 답변은 30단어 이내로 친절하게 작성하세요.\n"
                    "{context}"
                    "Question: {question}\n"
                    "Answer:"
                ),
                input_variables=["context", "question"]
            )

            llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
                callback_manager=callback_manager
            )
            pinecone_vectorstore = PineconeVectorStore(
                index=pinecone_index,  # ✅ Pinecone 클라이언트에서 생성한 Index 객체
                embedding=embeddings,  # ✅ OpenAI Embeddings 객체 전달
                text_key="text",  # ✅ 저장된 텍스트 키 (예: "text" 필드)
                namespace="",  # ✅ 필요한 경우 네임스페이스 사용
            )
            if exhibition_id:
                # exhibition_id가 있는 경우: RetrievalQA 체인 사용

                retriever = pinecone_vectorstore.as_retriever(search_kwargs={
                    "filter": {"exhibition_id": exhibition_id}
                })
                # ✅ Pinecone에서 검색된 문서 확인
                search_results = retriever.invoke(user_message)
                print(f"🔍 Exhibition {exhibition_id}에 대한 검색 결과:")
                for doc in search_results:
                    print(doc.metadata)  # ✅ 메타데이터 확인
                    print(doc.page_content)  # ✅ 저장된 텍스트 확인
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    chain_type_kwargs={"prompt": prompt_template}
                )

                def run_chain():
                    try:
                        # 이하 로직에서 토큰은 callback_manager를 통해 실시간 전송
                        qa_chain.invoke({"query": user_message})
                    except Exception as e:
                        token_queue.put(f"[error] {str(e)}")
                    finally:
                        token_queue.put(None)

                thread = threading.Thread(target=run_chain)
                thread.start()

            else:
                # exhibition_id가 없는 경우: RetrievalQA 없이 바로 LLM 호출
                def run_chain():
                    try:
                        # 아래 한 줄이 핵심: llm(...) 호출 시 streaming=True 이므로
                        # on_llm_new_token 콜백이 계속해서 token_queue에 토큰을 넣어줍니다.
                        llm.invoke(prompt_template.format(context="", question=user_message))
                    except Exception as e:
                        token_queue.put(f"[error] {str(e)}")
                    finally:
                        token_queue.put(None)

                thread = threading.Thread(target=run_chain)
                thread.start()

            # token_queue에 들어오는 토큰을 SSE 형태로 yield
            while True:
                token = token_queue.get()
                if token is None:
                    break
                yield f"data: {token}\n\n"
            thread.join()

        response = StreamingHttpResponse(event_stream(user_message), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        return response

    except Exception as e:
        return StreamingHttpResponse(
            f"data: {{\"error\": \"{str(e)}\"}}\n\n",
            content_type="text/event-stream",
            status=500
        )

def vectorize_text(text):
    # 실제 문장 임베딩 모델을 사용하여 임베딩 벡터를 생성하는 코드로 대체하세요.
    return [0.0] * 768

def add_to_vector_db(document, content):
    """
    업로드된 문서(document)의 텍스트(content)를 임베딩하여 Pinecone 인덱스에 저장합니다.
    문서에는 exhibition_id를 메타데이터로 저장하여 전시회별 검색이 가능하도록 합니다.
    """
    # OpenAI 임베딩을 통해 텍스트 임베딩 생성
    vector = embeddings.embed_query(content)
    # 각 문서의 고유 id (문서 모델의 pk를 사용)
    vector_id = f"doc_{document.id}"
    # 메타데이터에 전시회 id와 원문 텍스트를 포함 (필터링에 사용)
    metadata = {
        "exhibition_id": str(document.exhibition.id),
        "text": content,
    }
    # ✅ 디버깅: 저장할 데이터 출력
    print(f"🔹 저장할 벡터 ID: {vector_id}")
    print(f"🔹 저장할 벡터 크기: {len(vector)}")
    print(f"🔹 저장할 메타데이터: {metadata}")
    # Pinecone 인덱스에 업서트
    pinecone_index.upsert(vectors=[(vector_id, vector, metadata)])
    print(f"문서 {document.id} (전시회 {document.exhibition.id})가 Pinecone에 저장되었습니다.")


def admin_page(request):
    gallery_form = GalleryForm(prefix="gal")
    exhibition_form = ExhibitionForm(prefix="exh")
    document_form = DocumentForm(prefix="doc")

    if request.method == "POST":
        if "submit_document" in request.POST:
            document_form = DocumentForm(request.POST, request.FILES, prefix="doc")
            if document_form.is_valid():
                uploaded_file = document_form.cleaned_data["file"]
                if not uploaded_file:
                    messages.error(request, "파일을 선택하지 않았습니다.")
                    return redirect("admin_page")

                content = uploaded_file.read().decode("utf-8")
                doc_instance = document_form.save(commit=False)
                doc_instance.content = content
                doc_instance.save()

                # ✅ Pinecone 벡터 DB 추가
                add_to_vector_db(doc_instance, content)

                messages.success(request, "문서가 성공적으로 업로드되었습니다.")
                return redirect("admin_page")

    exhibitions = Exhibition.objects.all().order_by("-id")
    documents = Document.objects.all().order_by("-created_at")
    galleries = Gallery.objects.all()

    context = {
        "gallery_form": gallery_form,
        "exhibition_form": exhibition_form,
        "document_form": document_form,
        "exhibitions": exhibitions,
        "documents": documents,
        "galleries": galleries,
    }
    return render(request, "chat/admin_page.html", context)