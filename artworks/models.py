from django.db import models

class Artwork(models.Model):  # ✅ 이 부분이 파일 최상단에 있어야 함
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title