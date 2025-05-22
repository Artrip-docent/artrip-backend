# reviews/views.py

from rest_framework import viewsets
from .models import Review
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
