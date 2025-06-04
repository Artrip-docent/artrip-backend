# reviews/models.py

from django.db import models
from exhibition.models import Exhibition
from django.conf import settings

class Review(models.Model):
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField()  # 1~5점
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author} - {self.exhibition.title}"

