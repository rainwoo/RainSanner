from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Asset
from .serializers import RegisterSerializer, AssetSerializer

class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    """
    queryset = User.objects.all()
    # 允许任何人访问这个接口（因为注册时用户还没有 Token）
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class AssetViewSet(viewsets.ModelViewSet):
    """
    资产管理的增删改查接口
    提供 list, create, retrieve, update, destroy 动作
    """
    serializer_class = AssetSerializer
    # 必须是登录用户才能访问
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        """
        重写查询集：只返回当前登录用户自己创建的资产。
        防止别人看到你的敏感扫描目标！
        """
        return Asset.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        重写创建逻辑：在保存数据时，自动将当前用户作为该资产的 owner。
        """
        serializer.save(owner=self.request.user)
