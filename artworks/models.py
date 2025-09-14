from django.db import models
from exhibition.models import Exhibition
from django.conf import settings

def get_next_artwork_id():
    """
    가장 높은 ID를 찾아 1을 더한 값을 반환합니다.
    """
    highest_artwork = Artwork.objects.all().order_by('-id').first()
    if highest_artwork:
        return highest_artwork.id + 1
    return 1  # 작품이 하나도 없을 경우 1부터 시작

class Artwork(models.Model):
    id = models.IntegerField(primary_key=True, default=get_next_artwork_id) # 자동 ID 할당
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)
    mood = models.CharField(max_length=255, blank=True, null=True)
    style = models.CharField(max_length=255, blank=True, null=True)
    technique = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True) # 기존 필드 유지
    image = models.ImageField(upload_to='artworks/', blank=True, null=True) # 새 이미지 필드
    created_at = models.DateTimeField(auto_now_add=True)

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
