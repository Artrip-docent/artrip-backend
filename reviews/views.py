from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Review, Exhibition
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        exhibition_id = self.request.query_params.get('exhibition')
        if exhibition_id is not None:
            queryset = queryset.filter(exhibition__id=exhibition_id)
        return queryset

    def perform_create(self, serializer):
        exhibition_id = self.request.data.get('exhibition')
        if not exhibition_id:
            raise ValidationError("exhibition ID is required")

        try:
            exhibition = Exhibition.objects.get(id=exhibition_id)
        except Exhibition.DoesNotExist:
            raise ValidationError("Exhibition not found")

        from django.contrib.auth.models import User
        author = User.objects.get(id=1)

        serializer.save(author=author, exhibition=exhibition)
