import httpx  # HTTP 클라이언트를 위한 라이브러리
import os
import openai
import json
from dotenv import load_dotenv
from collections import Counter

def call_clip_model(image):
    """
    CLIP AI 모델과 통신하여 이미지를 분석하는 함수.
    """
    try:
        # AI 모델 서버 URL (환경 변수 또는 settings에서 관리 가능)
        AI_MODEL_URL = "http://clip-server/analyze"

        # 서버로 이미지 전송
        response = httpx.post(AI_MODEL_URL, files={"image": image}) # AI_MODEL_URL 부분 실제 CLIP 모델 url로 수정 요망
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # 모델에서 반환한 JSON 데이터
        return response.json()
    except httpx.HTTPError as e:
        print(f"AI 모델 호출 실패: {e}")
        return None  # 예외 발생 시 None 반환

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_tags_from_gpt(title, description):
    prompt = f"""
다음 작품의 제목과 설명을 참고하여, 사조(style)와 분위기(mood) 태그를 추출해줘.
모르면 최대한 일반적인 추측을 해도 돼.

제목: {title}
설명: {description}

아래와 같은 JSON 형식으로 응답해줘:
{{
  "style": ["사조1", "사조2"],
  "mood": ["분위기1", "분위기2"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        message = response.choices[0].message.content
        tags = json.loads(message)  # GPT 응답을 JSON으로 파싱
        return tags

    except Exception as e:
        print(f"❌ GPT 태그 추출 실패: {e}")
        return {"style": [], "mood": []}
