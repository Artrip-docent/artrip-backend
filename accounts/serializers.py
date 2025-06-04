from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password', 'nickname', 'gender')
        extra_kwargs = {'gender': {'required': False}}  # gender 필드를 models.py에 추가하면 필요

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            nickname=validated_data.get('nickname', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password) # 내부적으로 email확인
        if user:
            return user
        raise serializers.ValidationError("아이디 또는 비밀번호가 틀렸습니다.")