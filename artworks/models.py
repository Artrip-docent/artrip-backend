from django.db import models
from exhibition.models import Exhibition
from django.conf import settings

class Artwork(models.Model):  # ✅ 이 부분이 파일 최상단에 있어야 함
    id = models.IntegerField(primary_key=True)  # 인덱스 파일과 일치하는 id
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    mood = models.CharField(max_length=255, blank=True, null=True)  # 예: "Calm", "Dramatic" 등
    style = models.CharField(max_length=255, blank=True, null=True)      # 예: "Renaissance", "Impressionism" 등
    technique = models.CharField(max_length=255, blank=True, null=True)  # 예: "Oil on canvas", "Tempera" 등
    image_url = models.URLField(blank=True, null=True)                   # 작품 이미지의 URL (선택 사항)
    created_at = models.DateTimeField(auto_now_add=True)                 # 레코드 생성 시간

    def __str__(self):
        return self.title

class ViewingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    view_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.artwork.title} ({self.exhibition.title})"


class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    content = models.TextField()
    is_fixed = models.BooleanField(default=False)  # 고정 설명인지 질의응답인지 구분
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}: {'고정설명' if self.is_fixed else '질의응답'}"