from django.db import models

class Gallery(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Exhibition(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='exhibitions')
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.gallery.name})"

class Document(models.Model):
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='documents')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exhibition.title} - {self.pk}"
