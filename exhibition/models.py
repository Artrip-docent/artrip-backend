from django.db import models
from accounts.models import CustomUser

class Gallery(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class Exhibition(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, related_name='exhibitions')
    image_url = models.TextField(blank=True, null=True)
    liked_users = models.ManyToManyField(CustomUser, related_name='liked_exhibitions', blank=True)

    def __str__(self):
        return self.title