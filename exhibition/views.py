from django.http import JsonResponse
from .models import Exhibition

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
