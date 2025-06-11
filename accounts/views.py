import os
import uuid
import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model

from Artrip.utils.token import get_tokens_for_user
from .serializers import RegisterSerializer, LoginSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


# 카카오 로그인 및 토큰 발급
@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_token_view(request):
    kakao_data = request.data  # {'email': ..., 'nickname': ..., 'profile_image': ...}

    nickname = kakao_data.get('nickname') or '여행자'
    profile_image = kakao_data.get('profile_image') or 'https://ui-avatars.com/api/?name=Guest&background=random&color=ffffff'

    temp_username = f"kakao_{uuid.uuid4().hex[:10]}"

    user, created = User.objects.get_or_create(username=temp_username, defaults={
        'nickname': nickname,
        'profile_image': profile_image,
    })

    if not created:
        updated = False
        if not user.nickname and nickname:
            user.nickname = nickname
            updated = True
        if not user.profile_image and profile_image:
            user.profile_image = profile_image
            updated = True
        if updated:
            user.save()

    tokens = get_tokens_for_user(user)
    return Response({
        'message': '카카오 로그인 성공',
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    })


# 유저 정보 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user
    profile_image_url = ''
    if user.profile_image:
        profile_image_url = request.build_absolute_uri(user.profile_image)

    logger.info(f"Profile image URL: {profile_image_url}")

    return Response({
        'email': user.email,
        'nickname': user.nickname,
        'profile_image': profile_image_url,
    })


# 리프레시 토큰으로 액세스 토큰 재발급
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


# 회원가입
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'message': '회원가입 성공',
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }, status=201)
    return Response(serializer.errors, status=400)


# 로그인
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        tokens = get_tokens_for_user(user)
        return Response({
            'message': '로그인 성공',
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        })
    return Response(serializer.errors, status=400)


# 프로필 업데이트 (닉네임 + 이미지 업로드)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile_view(request):
    user = request.user

    # 닉네임 처리
    nickname = request.data.get('nickname')
    if nickname:
        user.nickname = nickname

    # 프로필 이미지 처리 (파일 저장 및 URL 저장)
    profile_image = request.FILES.get('profileImage')
    if profile_image:
        # media/profile_images/ 아래에 저장
        save_path = os.path.join('profile_images', profile_image.name)
        path = default_storage.save(save_path, ContentFile(profile_image.read()))

        # URL 필드에 media URL과 경로 합쳐서 저장 (ex: /media/profile_images/filename.jpg)
        user.profile_image = settings.MEDIA_URL + path

    user.save()
    return Response({'message': '프로필이 업데이트 되었습니다.'})
