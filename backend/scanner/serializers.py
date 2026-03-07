# backend/scanner/serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Asset
from .models import ScanTask, Vulnerability

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
    
class AssetSerializer(serializers.ModelSerializer):
    """资产序列化器"""
    class Meta:
        model = Asset
        fields = '__all__' # 暴露所有字段
        # 将 owner 设置为只读，前端不需要传这个字段，后端会自动根据当前登录用户去绑定
        read_only_fields = ('owner',)

class ScanTaskSerializer(serializers.ModelSerializer):
    """扫描任务序列化器"""
    # 跨表获取关联的资产名称和目标地址，设为只读
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_target = serializers.CharField(source='asset.target', read_only=True)

    class Meta:
        model = ScanTask
        fields = '__all__'

class VulnerabilitySerializer(serializers.ModelSerializer):
    """漏洞结果序列化器"""
    class Meta:
        model = Vulnerability
        fields = '__all__'