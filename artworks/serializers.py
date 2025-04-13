# artworks/serializers.py
from rest_framework import serializers
from .models import Artwork

class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'description', 'image_url']
