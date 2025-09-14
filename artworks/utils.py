import httpx  # HTTP 클라이언트를 위한 라이브러리
import os
import openai
import json
from dotenv import load_dotenv
from collections import Counter
import torch
from PIL import Image
import numpy as np
import faiss
from django.apps import apps
from django.conf import settings

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
    # 설명이 비어 있거나 None인 경우를 처리
    if not description or description.strip() == "":
        description_text = "설명이 제공되지 않았어. 제목만 참고해서 일반적인 사조와 분위기를 예측해줘."
    else:
        description_text = description

    prompt = f"""
다음 작품의 제목과 설명을 참고하여, 사조(style)와 분위기(mood) 태그를 추출해줘.
모르면 최대한 일반적인 추측을 해도 돼.

제목: {title}
설명: {description_text}

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
        tags = json.loads(message)
        return tags

    except Exception as e:
        print(f"❌ GPT 태그 추출 실패: {e}")
        return {"style": [], "mood": []}

def add_artwork_to_index(artwork_instance):
    """
    새로운 작품을 Faiss 인덱스에 추가하고 파일로 저장합니다.
    """
    # 1. AppConfig에서 Faiss 인덱스, artwork_ids, CLIP 모델 등을 가져옴
    config = apps.get_app_config('artworks')
    if config.faiss_index is None or config.artwork_ids is None:
        print("❌ Faiss index not loaded.")
        return

    model = config.clip_model
    preprocess = config.clip_preprocess
    device = config.device
    index = config.faiss_index
    artwork_ids = config.artwork_ids

    # 2. 새로 추가된 작품의 이미지 벡터화
    try:
        image = Image.open(artwork_instance.image.path).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model.encode_image(image_input)
        
        # 벡터 정규화
        features /= features.norm(dim=-1, keepdim=True)
        new_vector = features.cpu().numpy()
    except Exception as e:
        print(f"❌ Image vectorization failed: {e}")
        return

    # 3. Faiss 인덱스 및 ID 배열 업데이트
    index.add(new_vector)
    
    new_artwork_id = artwork_instance.id
    artwork_ids = np.append(artwork_ids, new_artwork_id)

    # 4. 변경된 인덱스와 ID 배열을 파일에 저장
    try:
        index_path = os.path.join(settings.BASE_DIR, 'indexes', 'artwork.index')
        ids_path = os.path.join(settings.BASE_DIR, 'indexes', 'artwork_ids.npy')

        faiss.write_index(index, index_path)
        np.save(ids_path, artwork_ids)

        config.faiss_index = index
        config.artwork_ids = artwork_ids

        print(f"✅ Artwork {new_artwork_id} added to Faiss index and saved to disk.")
        print(f"Total vectors in index: {index.ntotal}")

    except Exception as e:
        print(f"❌ Failed to save Faiss index or IDs: {e}")