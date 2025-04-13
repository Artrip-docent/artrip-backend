from django.urls import path
from .views import UploadArtworkView
from .views import UploadArtworkView, AnalyzePreferenceView
from .views import UploadArtworkView, RandomArtworksView


urlpatterns = [
    path("", UploadArtworkView.as_view(), name="upload-artwork"),  # http://127.0.0.1:8000/artworks/ 로 접근
    path("upload/", UploadArtworkView.as_view(), name="upload-artwork"),  # http://127.0.0.1:8000/artworks/upload/

    path("analyze-preference/", AnalyzePreferenceView.as_view(), name="analyze-preference"),

    path("random/", RandomArtworksView.as_view(), name="random-artworks"),


]