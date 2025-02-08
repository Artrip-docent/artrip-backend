from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser  # 이미지 업로드 처리를 위한 파서
from rest_framework import status
import random # 랜덤 데이터 선택 목적(mock data 테스트용)
# from .utils import call_clip_model  # CLIP 모델 호출 함수
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class AnalyzeImageView(APIView):

    parser_classes = [MultiPartParser]

    # Mock 데이터: 임의로 저장한 5개의 작품 정보
    MOCK_ARTWORKS = [
        {
            "artwork_id": 1,
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": 1503,
            "style": "Renaissance",
            "description": "A portrait of a woman with a mysterious smile, considered a masterpiece of Renaissance art.",
        },
        {
            "artwork_id": 2,
            "title": "Starry Night",
            "artist": "Vincent van Gogh",
            "year": 1889,
            "style": "Post-Impressionism",
            "description": "A depiction of Van Gogh's view from the asylum, featuring swirling stars and a bright moon.",
        },
        {
            "artwork_id": 3,
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "year": 1931,
            "style": "Surrealism",
            "description": "This surreal painting features melting clocks draped over a barren landscape, symbolizing the fluidity of time.",
        },
        {
            "artwork_id": 4,
            "title": "The Scream",
            "artist": "Edvard Munch",
            "year": 1893,
            "style": "Expressionism",
            "description": "An iconic artwork capturing existential angst, with a figure screaming on a bridge under a blood-red sky.",
        },
        {
            "artwork_id": 5,
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": 1486,
            "style": "Renaissance",
            "description": "This masterpiece depicts the goddess Venus emerging from the sea on a shell, representing divine beauty and love.",
        }
    ]

    def get(self, request):
        # 1. Mock 데이터에서 랜덤으로 작품 선택
        artwork = random.choice(self.MOCK_ARTWORKS)

        # 2. 응답 데이터 반환
        return Response({
            "artwork_name": artwork["title"],
            "artist": artwork["artist"]
        }, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class UploadArtworkView(APIView):
        """
        사용자로부터 이미지를 업로드받고 Mock 데이터를 반환하는 API.
        """
        parser_classes = [MultiPartParser]  # 이미지 업로드 처리를 위한 설정

        # Mock 데이터: 임의로 저장한 5개의 작품 정보
        MOCK_ARTWORKS = [
        {
            "artwork_id": 1,
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": 1503,
            "style": "Renaissance",
            "description": "A portrait of a woman with a mysterious smile, considered a masterpiece of Renaissance art.",
        },
        {
            "artwork_id": 2,
            "title": "Starry Night",
            "artist": "Vincent van Gogh",
            "year": 1889,
            "style": "Post-Impressionism",
            "description": "A depiction of Van Gogh's view from the asylum, featuring swirling stars and a bright moon.",
        },
        {
            "artwork_id": 3,
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "year": 1931,
            "style": "Surrealism",
            "description": "This surreal painting features melting clocks draped over a barren landscape, symbolizing the fluidity of time.",
        },
        {
            "artwork_id": 4,
            "title": "The Scream",
            "artist": "Edvard Munch",
            "year": 1893,
            "style": "Expressionism",
            "description": "An iconic artwork capturing existential angst, with a figure screaming on a bridge under a blood-red sky.",
        },
        {
            "artwork_id": 5,
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": 1486,
            "style": "Renaissance",
            "description": "This masterpiece depicts the goddess Venus emerging from the sea on a shell, representing divine beauty and love.",
        }
        ]

        def post(self, request):
            # 1. 이미지 파일 검증
            uploaded_image = request.FILES.get('image')
            if not uploaded_image:
                return Response({"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Mock 데이터에서 랜덤으로 작품 선택
            artwork = random.choice(self.MOCK_ARTWORKS)

            # 3. 응답 데이터 반환 (이미지는 일단 무시)
            return Response({
                "message": "Mock data returned.",
                "artwork_name": artwork["title"],
                "artist": artwork["artist"],
                "year": artwork["year"],
                "style": artwork["style"],
                "description": artwork["description"],  # 고정 설명 추가
                "uploaded_filename": uploaded_image.name,  # 업로드된 파일 이름 반환 (테스트용)
            }, status=status.HTTP_200_OK)

"""
class UploadArtworkView(APIView):
    # 사용자로부터 이미지를 업로드받고, AI 모델에 전달하여 결과를 반환하는 API.
    parser_classes = [MultiPartParser]  # 이미지 업로드 처리를 위한 설정

    def post(self, request):
        # 1. 이미지 파일 검증
        uploaded_image = request.FILES.get('image')
        if not uploaded_image:
            return Response({"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. AI 모델 호출
        # 이 부분은 나중에 캐싱 로직 또는 여러 모델 호출 로직으로 확장 가능
        ai_response = call_clip_model(uploaded_image)
        if not ai_response:
            return Response({"error": "AI model failed to process the image."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. 응답 데이터 구성
        # 나중에 작품 데이터베이스 연동이 필요할 경우, 여기서 DB에서 작품 정보를 가져와 추가 가능
        response_data = {
            "message": "Image processed successfully!",
            "ai_response": ai_response,  # AI 모델에서 반환한 결과
        }

        return Response(response_data, status=status.HTTP_200_OK)
"""