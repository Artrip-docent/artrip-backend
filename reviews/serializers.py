from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'exhibition', 'author', 'author_name', 'content', 'rating', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at']
