from django.urls import path
from .views import kakao_token_view, user_info_view, register_view, login_view, update_profile_view, complete_preference_view
from .views import CustomTokenRefreshView

urlpatterns = [
    path('register/', register_view),
    path('login/', login_view),
    path('kakao/token/', kakao_token_view),
    path('user/', user_info_view),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('update-profile/', update_profile_view),
    path('user-info/', user_info_view, name='user-info'),
    path('complete-preference/', complete_preference_view, name='complete-preference'),
]
