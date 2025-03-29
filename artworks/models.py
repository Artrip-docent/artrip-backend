from django.db import models

class Artwork(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.artist}"