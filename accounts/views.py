# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from Artrip.utils.token import get_tokens_for_user
from .models import UserProfile

# 1. 카카오 로그인 후 토큰 발급
@api_view(['GET'])
@permission_classes([AllowAny])
@login_required
def kakao_token_view(request):
    user = request.user
    tokens = get_tokens_for_user(user)
    return Response({
        'message': '카카오 로그인 성공',
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    })

# 2. 사용자 정보 반환 API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user
    profile = getattr(user, 'userprofile', None)
    return Response({
        'email': user.email,
        'name': profile.name if profile else '',
        'gender': profile.gender if profile else '',
    })

# 3. 추가 프로필 입력 여부 확인 API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def need_profile_view(request):
    user = request.user
    need_profile = not hasattr(user, 'userprofile')
    return Response({
        'need_profile': need_profile
    })

# 4. 추가정보 등록 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_profile_view(request):
    user = request.user

    if hasattr(user, 'userprofile'):
        return Response({'message': '이미 프로필이 등록되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    name = request.data.get('name')
    gender = request.data.get('gender')

    if not name or not gender:
        return Response({'message': '이름과 성별은 필수입니다.'}, status=status.HTTP_400_BAD_REQUEST)

    profile = UserProfile.objects.create(user=user, name=name, gender=gender)
    return Response({'message': '프로필 등록 완료'})

# 5. Refresh 토큰으로 Access 재발급 API
class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /auth/token/refresh/
    Body: { "refresh": "<your_refresh_token>" }
    → Response: { "access": "<new_access_token>" }
    """
    permission_classes = [AllowAny]