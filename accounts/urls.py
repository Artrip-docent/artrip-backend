# accounts/urls.py
from django.urls import path
from .views import kakao_token_view,register_profile_view, user_info_view, need_profile_view
from .views import CustomTokenRefreshView
urlpatterns = [
    path('kakao/token/', kakao_token_view),
    path('user/', user_info_view),
    path('user/need-profile/', need_profile_view),
    path('user/profile/', register_profile_view),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
