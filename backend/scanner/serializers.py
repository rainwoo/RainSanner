# backend/scanner/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """用于展示用户信息的序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    """用于处理用户注册的序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        # 设置 password 为只写，这样返回用户信息时就不会包含密码，保证安全
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 使用 create_user 方法创建用户，它会自动帮我们对密码进行加密处理
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user