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
# --- LangChain 관련 임포트 ---
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler

# 예시 문서 리스트 (실제 서비스에 맞게 교체)
docs = [
    "작품 A는 19세기 유럽의 대표적인 인상주의 작품으로, 빛과 색채의 조화가 돋보입니다.",
    "작품 B는 현대 미술의 경향을 보여주며, 감정의 표현과 추상적 형상이 특징입니다.",
]

# OpenAI Embeddings를 사용하여 벡터스토어 구축 (한 번만 초기화하는 것이 좋습니다)
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
vectorstore = FAISS.from_texts(docs, embeddings)

# Swagger 요청 및 응답 정의
message_param = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(type=openapi.TYPE_STRING, description="User message")
    },
    required=["message"],
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
    operation_description="GPT-4o와 대화하며 SSE로 응답을 스트리밍합니다.",
)
@api_view(["POST"])
@csrf_exempt
def chat_view(request):
    """
    작품 도슨트 역할을 수행하는 AI 챗봇.
    사용자 입력에 대해 친절하게 30단어 이내의 설명을 반환하며,
    GPT의 응답을 SSE로 스트리밍합니다.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        if not user_message:
            return StreamingHttpResponse(
                "data: {\"error\": \"Message cannot be empty\"}\n\n",
                content_type="text/event-stream",
                status=400
            )

        def event_stream(user_message):
            # 토큰을 전달할 큐 생성
            token_queue = queue.Queue()

            # SSE 전송을 위한 사용자 정의 콜백 핸들러
            class SSECallbackHandler(BaseCallbackHandler):
                def on_llm_new_token(self, token: str, **kwargs) -> None:
                    token_queue.put(token)

            callback_handler = SSECallbackHandler()
            callback_manager = CallbackManager([callback_handler])

            # 프롬프트 템플릿 정의
            prompt_template = PromptTemplate(
                template=(
                    "당신은 작품 도슨트입니다. 모든 답변은 30단어 이내로 친절하게 작성하세요.\n"
                    "다음 문맥을 참고하여 질문에 답변하세요.\n\n"
                    "Context: {context}\n"
                    "Question: {question}\n"
                    "Answer:"
                ),
                input_variables=["context", "question"]
            )

            # 스트리밍 기능을 활성화한 LLM 초기화
            llm = ChatOpenAI(
                model_name="gpt-4o-mini",   # 🔥 gpt-4o → gpt-4o-mini 로 변경
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
                callback_manager=callback_manager
            )

            # RetrievalQA 체인 생성
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": prompt_template}
            )

            # 체인 실행은 별도 스레드에서 수행
            result = {}

            def run_chain():
                nonlocal result
                try:
                    result = qa_chain({"query": user_message})
                except Exception as e:
                    token_queue.put(f"[error] {str(e)}")
                finally:
                    # 체인 실행 완료 후, sentinel 값을 넣어 반복문 종료 신호 전달
                    token_queue.put(None)

            thread = threading.Thread(target=run_chain)
            thread.start()

            # 토큰 큐에서 하나씩 가져와 SSE 이벤트로 전송
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
        # 스트리밍 시작 전 발생한 오류 처리
        return StreamingHttpResponse(
            f"data: {{\"error\": \"{str(e)}\"}}\n\n",
            content_type="text/event-stream",
            status=500
        )