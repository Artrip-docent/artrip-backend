from django.urls import path
from .views import AnalyzeImageView  # AnalyzeImageView를 임포트(mock)
from .views import UploadArtworkView

urlpatterns = [
    path('analyze-image/', AnalyzeImageView.as_view(), name='analyze_image'),
    path('upload-artwork/', UploadArtworkView.as_view(), name='upload_artwork'),  # 이미지 업로드 경로
]

""""
urlpatterns = [
    path('upload/', UploadArtworkView.as_view(), name='upload_artwork'),  # 이미지 업로드 API 엔드포인트
]
"""