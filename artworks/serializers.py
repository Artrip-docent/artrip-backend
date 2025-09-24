# artworks/serializers.py
from rest_framework import serializers
from .models import Artwork, ViewingHistory
from exhibition.models import Exhibition
from exhibition.serializers import ExhibitionHistorySerializer


class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'description', 'image_url']

class ViewingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewingHistory
        fields = '__all__'

class ViewedArtworkSerializer(serializers.ModelSerializer):
    exhibition = serializers.SerializerMethodField()

    class Meta:
        model = Artwork
        fields = ['id', 'title', 'image_url', 'exhibition']

    def get_exhibition(self, obj):
        exhibition = self.context.get('exhibition')
        if exhibition:
            return ExhibitionHistorySerializer(exhibition).data
        return None