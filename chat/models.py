from django.db import models
from exhibition.models import Exhibition # Import the one true Exhibition model

class Document(models.Model):
    # ForeignKey now points to the consolidated Exhibition model
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='documents')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exhibition.title} - {self.pk}"
