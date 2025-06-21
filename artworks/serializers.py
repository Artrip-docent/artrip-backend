# artworks/serializers.py
from rest_framework import serializers
from .models import Artwork, ViewingHistory

class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'description', 'image_url']

class ViewingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewingHistory
        fields = '__all__'