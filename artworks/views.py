# artworks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.apps import apps
from io import BytesIO
from PIL import Image
import torch

# Artwork 모델: DB의 작품 메타데이터에 대응
from .models import Artwork

class UploadArtworkView(APIView):
    """
    사용자가 업로드한 이미지 CLIP으로 벡터화하고
    Faiss 인덱스를 통해 유사 작품 id를 찾은 후 db에서 해당 작품 정보를 조회하여 반환하는 API
    """
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 1. 업로드된 이미지 파일이 있는지 확인
        uploaded_file = request.FILES.get('image')
        if not uploaded_file:
            return Response({"error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. AppConfig에서 Faiss 인덱스, artwork_ids, CLIP 모델 및 전처리 객체를 가져옴
        config = apps.get_app_config('artworks')
        if config.faiss_index is None or config.artwork_ids is None:
            return Response({"error": "Faiss index not loaded."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        model = config.clip_model
        preprocess = config.clip_preprocess
        device = config.device
        index = config.faiss_index
        artwork_ids = config.artwork_ids

        # 3. 업로드된 이미지를 PIL로 열고, RGB로 변환
        try:
            image = Image.open(BytesIO(uploaded_file.read())).convert("RGB")
        except Exception as e:
            return Response({"error": "Invalid image file."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. CLIP 모델로 이미지 벡터화
        image_input = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            features = model.encode_image(image_input)
        # 벡터 정규화 (코사인 유사도 계산을 위함)
        features = features / features.norm(dim=-1, keepdim=True)
        query_vector = features.cpu().numpy()

        # 5. Faiss 인덱스 검색: 상위 1개의 결과 찾기
        distances, indices = index.search(query_vector, 1)
        best_idx = indices[0][0]
        best_artwork_id = int(artwork_ids[best_idx])

        # 6. DB에서 해당 artwork_id에 해당하는 작품 정보 조회
        try:
            artwork = Artwork.objects.get(id=best_artwork_id)
            data = {
                "artwork_id": artwork.id,
                "title": artwork.title,             # 혹은 기존에 쓰던 "artwork_name"
                "artist": artwork.artist,
                "year": artwork.year,
                "description": artwork.description,
                "style": artwork.style,
                "mood": artwork.mood,
                "technique": artwork.technique,
                "image_url": artwork.image_url,
                "created_at": artwork.created_at.isoformat(),
            }
        except Artwork.DoesNotExist:
            data = {"error": f"Artwork with id {best_artwork_id} not found in DB."}

        return Response(data, status=status.HTTP_200_OK)