from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import json
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    operation_description="Chat with OpenAI GPT-4o-mini and receive a short response as a docent.",
)
@api_view(["POST"])
@csrf_exempt
def chat_view(request):
    """
    작품 도슨트 역할을 수행하는 AI 챗봇.
    사용자 입력에 대해 친절하게 30단어 이내의 설명을 반환합니다.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")

        if not user_message:
            return Response({"error": "Message cannot be empty"}, status=400)

        # 시스템 프롬프트 추가
        system_prompt = {
            "role": "system",
            "content": (
                "당신은 작품 도슨트입니다. "
                "모든 답변은 친절한 어조로 30단어 이내의 한국어로 작성하세요. "
                "사용자가 작품에 대해 물어보면 핵심적인 정보를 간결하게 제공하세요."
            )
        }

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 작품 도슨트입니다. 30단어 이내로 친절하게 답하세요."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_response = response.choices[0].message.content

        return Response({"response": bot_response})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
