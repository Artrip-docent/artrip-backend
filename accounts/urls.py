from django.urls import path
from .views import kakao_token_view, user_info_view,register_view, login_view
from .views import CustomTokenRefreshView, update_nickname_view, update_profile_image_view

urlpatterns = [
    path('register/', register_view),
    path('login/', login_view),
    path('kakao/token/', kakao_token_view),
    path('user/', user_info_view),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
path('nickname/', update_nickname_view),
    path('profile-image/', update_profile_image_view),
]
