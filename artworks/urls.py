from django.urls import path
from .views import UploadArtworkView

urlpatterns = [
    path("", UploadArtworkView.as_view(), name="upload-artwork"),  # http://127.0.0.1:8000/artworks/ 로 접근
    path("upload/", UploadArtworkView.as_view(), name="upload-artwork"),  # http://127.0.0.1:8000/artworks/upload/
]