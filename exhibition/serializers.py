from rest_framework import serializers
from .models import Exhibition, Gallery


class ExhibitionHistorySerializer(serializers.ModelSerializer):
    gallery = serializers.CharField(source='gallery.name')
    location = serializers.CharField(source='gallery.name')

    class Meta:
        model = Exhibition
        fields = ('gallery', 'location')


class ExhibitionSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='gallery.name', read_only=True)

    class Meta:
        model = Exhibition
        fields = ['id', 'title', 'start_date', 'end_date', 'image_url', 'liked_users', 'location']
