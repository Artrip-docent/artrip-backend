from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from .models import Review, Exhibition
from .serializers import ReviewSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# 작성자만 수정/삭제 허용(조회는 모두 허용)
class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET/HEAD/OPTIONS
        if request.method in SAFE_METHODS:
            return True
        # author_id 또는 obj.author.id 비교
        author_id = getattr(obj, "author_id", None)
        if author_id is None and hasattr(obj, "author"):
            author_id = getattr(obj.author, "id", None)
        return author_id == getattr(request.user, "id", None)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # 조회 → 허용 / 생성 → 로그인 / 수정·삭제 → 로그인 + 작성자
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    # ?exhibition=<id> 필터
    def get_queryset(self):
        qs = super().get_queryset()
        exhibition_id = self.request.query_params.get("exhibition")
        if exhibition_id:
            qs = qs.filter(exhibition__id=exhibition_id)
        return qs

    # 생성 시 author 고정 + 전시 존재 검증
    def perform_create(self, serializer):
        exhibition_id = self.request.data.get("exhibition")
        if not exhibition_id:
            raise ValidationError("exhibition ID is required")
        try:
            exhibition = Exhibition.objects.get(id=exhibition_id)
        except Exhibition.DoesNotExist:
            raise ValidationError("Exhibition not found")
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        serializer.save(author=self.request.user, exhibition=exhibition)

    # 수정 시에도 작성자 재검증
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author_id != self.request.user.id:
            raise PermissionDenied("본인 리뷰만 수정할 수 있습니다.")
        serializer.save(author=instance.author, exhibition=instance.exhibition)

    # 삭제 시에도 작성자 재검증
    def perform_destroy(self, instance):
        if instance.author_id != self.request.user.id:
            raise PermissionDenied("본인 리뷰만 삭제할 수 있습니다.")
        super().perform_destroy(instance)

