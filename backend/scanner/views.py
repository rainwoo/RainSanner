from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    """
    queryset = User.objects.all()
    # 允许任何人访问这个接口（因为注册时用户还没有 Token）
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
