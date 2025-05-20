# artworks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.apps import apps
from io import BytesIO
from PIL import Image
import torch
from .utils import extract_tags_from_gpt
from collections import Counter
from .serializers import ArtworkSerializer
import random
from chat.mongo_utils import save_info
from .models import ViewingHistory
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

        """
            관람 이력에 사용자 아이디, 전시회 아이디 기록
        """
        exhibition_id = request.data.get('exhibition_id')
        user_id = request.data.get('user_id')
        if not exhibition_id or not user_id:
            return Response({"error": "exhibition_id와 user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

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
                "artwork_name": artwork.title,
                "artist": artwork.artist,
                "year": artwork.year,
                "description": artwork.description,
            }

            # 관람이력 (-> MySQL)
            ViewingHistory.objects.create(
                user_id=user_id,
                exhibition_id=exhibition_id,
                artwork=artwork
            )

            initial_message = f"""
                        🎨 작품 정보 🎨
                        제목: {artwork.title}
                        작가: {artwork.artist}
                        연도: {artwork.year}

                        📝 설명:
                        {artwork.description}
                        """.strip()
            save_info(user_id=user_id, exhibition_id=exhibition_id,
                      artwork_id=artwork.id, info_text=initial_message)

        except Artwork.DoesNotExist:
            # ✅ artwork 없음 처리
            data = {"error": f"Artwork with id {best_artwork_id} not found in DB."}
            save_info(user_id=user_id, exhibition_id=exhibition_id,
                      artwork_id=1, info_text="기본 정보 없음 (id not found)")

        return Response(data, status=status.HTTP_200_OK)

# 사용자 취향을 누적 저장할 수 있는 임시 전역 딕셔너리
user_preferences_store = {
    # 예: "user1": {"style": Counter(...), "mood": Counter(...)}
}
class AnalyzePreferenceView(APIView):
    def post(self, request):
        print("✅ [ANALYZE] 요청 데이터:", request.data)
        user_id = request.data.get("user_id", "default_user")
        artwork_ids = request.data.get("artwork_ids", [])
        if not artwork_ids:
            return Response({"error": "작품 ID 목록이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        styles, moods = [], []

        for artwork in Artwork.objects.filter(id__in=artwork_ids):
            tags = extract_tags_from_gpt(artwork.title, artwork.description or "")
            styles.extend(tags.get("style", []))
            moods.extend(tags.get("mood", []))

        # ✅ style + mood 통합 후 카운팅
        combined_tags = styles + moods
        tag_counter = Counter(combined_tags)
        top_tags = tag_counter.most_common(5)

        print("🎨 상위 5개 통합 태그:", top_tags)

        return Response({
            "top_tags": [tag for tag, _ in top_tags]  # 문자열 리스트로만 반환
        }, status=status.HTTP_200_OK)

class RandomArtworksView(APIView): # 랜덤 작품 뷰 추가
    def get(self, request):
        artworks = list(Artwork.objects.all())
        random_artworks = random.sample(artworks, min(len(artworks), 4))  # 최대 4개 랜덤
        serializer = ArtworkSerializer(random_artworks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





