from django.urls import path
from .views import (
    exhibition_list,
    exhibition_list_sorted_for_user,
    toggle_like,
    search_exhibitions,
)

urlpatterns = [
    path('', exhibition_list, name='exhibition-list'),
    path('sorted-user/', exhibition_list_sorted_for_user, name='exhibition-sorted-user'),  # 좋아요 누른 전시 우선정렬
    path('toggle-like/', toggle_like, name='toggle-like'),  # 좋아요 토글
    path('search/', search_exhibitions, name='search-exhibitions'),  # 검색 기능
]