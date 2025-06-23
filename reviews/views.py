from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Review, Exhibition
from .serializers import ReviewSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [AllowAny()]  # 조회는 모두 허용
        return [IsAuthenticated()]  # 생성, 수정, 삭제 등은 인증 필요

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

        author = self.request.user
        print(f"[DEBUG] user: {author}, authenticated: {author.is_authenticated}")
        if not author.is_authenticated:
            raise PermissionDenied("Authentication required")

        serializer.save(author=author, exhibition=exhibition)
