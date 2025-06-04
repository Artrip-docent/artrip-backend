from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from Artrip.utils.token import get_tokens_for_user
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# ✅ 카카오 로그인 및 토큰 발급
@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_token_view(request):
    kakao_data = request.data  # {'email': ..., 'nickname': ..., 'profile_image': ...}

    # email = kakao_data.get('email') # 이메일은 현재 받을 수 없는 상태
    nickname = kakao_data.get('nickname') or '여행자'
    profile_image = kakao_data.get('profile_image') or 'https://ui-avatars.com/api/?name=Guest&background=random&color=ffffff'

    # 임시로 이메일 대신 username을 랜덤 문자열로 생성 (혹은 카카오 ID 등을 써도 됨)
    import uuid
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


# ✅ 유저 정보 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user
    return Response({
        'email': user.email,
        'nickname': user.nickname,
        'profile_image': user.profile_image,
    })


# ✅ 리프레시 토큰으로 액세스 토큰 재발급
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]



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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_nickname_view(request):
    new_nickname = request.data.get('nickname')
    if not new_nickname:
        return Response({'error': '닉네임을 입력해주세요.'}, status=400)

    user = request.user
    user.nickname = new_nickname
    user.save()
    return Response({'message': '닉네임이 변경되었습니다.', 'nickname': user.nickname})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_image_view(request):
    new_image_url = request.data.get('profile_image')
    if not new_image_url:
        return Response({'error': '프로필 이미지 URL을 입력해주세요.'}, status=400)

    user = request.user
    user.profile_image = new_image_url
    user.save()
    return Response({'message': '프로필 이미지가 변경되었습니다.', 'profile_image': user.profile_image})
