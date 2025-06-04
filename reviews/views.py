from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Review, Exhibition
from .serializers import ReviewSerializer
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ 커스텀 유저 모델 적용

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

        # ✅ 임시 테스트 코드: id=1 유저
        author = User.objects.get(id=1)

        serializer.save(author=author, exhibition=exhibition)
