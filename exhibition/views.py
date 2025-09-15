from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.db.models import Case, When, Value, IntegerField, Q
from django.utils import timezone

from .models import Exhibition

User = get_user_model()


# 좋아요 토글 api
@csrf_exempt
@require_POST
def toggle_like(request):
    try:
        body = json.loads(request.body)
        user_id = body.get("user_id")
        exhibition_id = body.get("exhibition_id")

        if not user_id or not exhibition_id:
            return JsonResponse({"error": "user_id와 exhibition_id 필요"}, status=400)

        user = get_object_or_404(User, id=user_id)
        exhibition = get_object_or_404(Exhibition, id=exhibition_id)

        if exhibition.liked_users.filter(id=user.id).exists():
            exhibition.liked_users.remove(user)
            liked = False
        else:
            exhibition.liked_users.add(user)
            liked = True

        return JsonResponse({"liked": liked})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON 파싱 실패"}, status=400)


# 좋아요 우선 + 진행중→예정→지난 + 시작일 오름차순
def exhibition_list_sorted_for_user(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({"error": "user_id 파라미터가 필요합니다."}, status=400)

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "user_id는 정수여야 합니다."}, status=400)

    today = timezone.localdate()

    exhibitions = (
        Exhibition.objects.select_related('gallery')
        .annotate(
            is_liked=Case(
                When(liked_users__id=user_id_int, then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            ),
            status_order=Case(
                When(end_date__lt=today, then=Value(2)),  # 지난
                When(start_date__lte=today, end_date__gte=today, then=Value(0)),  # 진행중
                When(start_date__gt=today, then=Value(1)),  # 예정
                default=Value(3),
                output_field=IntegerField()
            ),
        )
        .order_by('is_liked', 'status_order', 'start_date', 'id')
        .distinct()
    )

    data = [
        {
            'id': e.id,
            'title': e.title,
            'period': f"{e.start_date} ~ {e.end_date}",
            'location': (e.gallery.name if e.gallery else ""),
            'imageUrl': e.image_url,
            'liked': (e.is_liked == 0),
        }
        for e in exhibitions
    ]
    return JsonResponse(data, safe=False)


# 전시회 검색(제목 기준) - 진행중→예정→지난 순 정렬, 응답 포맷은 기존과 동일(image_url)
def search_exhibitions(request):
    query = request.GET.get('q', '').strip()
    today = timezone.localdate()

    exhibitions = (
        Exhibition.objects.select_related('gallery')
        .filter(Q(title__icontains=query))
        .annotate(
            status_order=Case(
                When(end_date__lt=today, then=Value(2)),  # 지난
                When(start_date__lte=today, end_date__gte=today, then=Value(0)),  # 진행중
                When(start_date__gt=today, then=Value(1)),  # 예정
                default=Value(3),
                output_field=IntegerField()
            )
        )
        .order_by('status_order', 'start_date', 'id')
        .distinct()
    )

    data = [
        {
            "id": e.id,
            "title": e.title,
            "period": f"{e.start_date} ~ {e.end_date}",
            "start_date": str(e.start_date),
            "end_date": str(e.end_date),
            "location": (e.gallery.name if e.gallery else ""),   # 널 방어
            "imageUrl": e.image_url,  # 목록과 동일 키
            "image_url": e.image_url, # 하위호환(둘 다 내려줌)
        }
        for e in exhibitions
    ]
    return JsonResponse(data, safe=False)  # ← 배열 루트로 통일


# 전체 전시 리스트
# 기본: ?scope=active → 지난 전시 제외
#       ?scope=all    → 모두 포함 (정렬은 동일: 진행중→예정→지난)
def exhibition_list(request):
    scope = request.GET.get('scope', 'active').lower()
    today = timezone.localdate()

    qs = (
        Exhibition.objects.select_related('gallery')
        .annotate(
            status_order=Case(
                When(end_date__lt=today, then=Value(2)),  # 지난
                When(start_date__lte=today, end_date__gte=today, then=Value(0)),  # 진행중
                When(start_date__gt=today, then=Value(1)),  # 예정
                default=Value(3),
                output_field=IntegerField()
            )
        )
    )

    if scope == 'active':
        qs = qs.filter(end_date__gte=today)  # 지난 전시 제외

    exhibitions = qs.order_by('status_order', 'start_date', 'id').distinct()

    data = [
        {
            'id': e.id,
            'title': e.title,
            'period': f"{e.start_date} ~ {e.end_date}",
            'location': (e.gallery.name if e.gallery else ""),
            'imageUrl': e.image_url,  # 기존 목록 응답 키(imageUrl) 유지
        }
        for e in exhibitions
    ]
    return JsonResponse(data, safe=False)
