from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.db.models import Case, When, Value, IntegerField, Q

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

        if user in exhibition.liked_users.all():
            exhibition.liked_users.remove(user)
            liked = False
        else:
            exhibition.liked_users.add(user)
            liked = True

        return JsonResponse({"liked": liked})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON 파싱 실패"}, status=400)

# 좋아요 누른 전시회 우선 정렬 api
def exhibition_list_sorted_for_user(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({"error": "user_id 파라미터가 필요합니다."}, status=400)

    # liked 전시회를 우선으로 정렬
    exhibitions = Exhibition.objects.annotate(
        is_liked=Case(
            When(liked_users__id=user_id, then=Value(0)),  # 좋아요한 전시는 0
            default=Value(1),  # 나머지는 1
            output_field=IntegerField()
        )
    ).order_by('is_liked', '-start_date')  # 좋아요 먼저, 최신순

    data = [
        {
            'id': e.id,
            'title': e.title,
            'period': f"{e.start_date} ~ {e.end_date}",
            'location': e.location,
            'imageUrl': e.image_url,
            'liked': (e.is_liked == 0)
        }
        for e in exhibitions
    ]
    return JsonResponse(data, safe=False)

# 전시회 검색(제목 기준) api (-> 하단 왼쪽 탭, 가운데 탭에 연동)
def search_exhibitions(request):
    query = request.GET.get('q', '')

    # 전시회 제목에서 검색어가 포함된 항목 찾기
    exhibitions = Exhibition.objects.filter(Q(title__icontains=query)).distinct()

    # JSON 형태로 응답
    data = [
        {
            'id': exhibition.id,
            'title': exhibition.title,
            'start_date': exhibition.start_date,
            'end_date': exhibition.end_date,
            'location': exhibition.location,
            'image_url': exhibition.image_url,
        }
        for exhibition in exhibitions
    ]

    return JsonResponse({'results': data}, status=200)

def exhibition_list(request):
    exhibitions = Exhibition.objects.all().values(
        'id', 'title', 'start_date', 'end_date', 'location', 'image_url'
    )

    # 날짜를 문자열로 변환해서 반환
    data = [
        {
            'id': e['id'],
            'title': e['title'],
            'period': f"{e['start_date']} ~ {e['end_date']}",
            'location': e['location'],
            'imageUrl': e['image_url'],
        }
        for e in exhibitions
    ]

    return JsonResponse(data, safe=False)