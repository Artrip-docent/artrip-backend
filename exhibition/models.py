from django.db import models
from accounts.models import CustomUser

class Exhibition(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    image_url = models.TextField(blank=True, null=True)
    liked_users = models.ManyToManyField(CustomUser, related_name='liked_exhibitions', blank=True)

    def __str__(self):
        return self.title