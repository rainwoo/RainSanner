from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 注册接口: http://127.0.0.1:8000/api/register/
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # 登录接口 (获取 Token): http://127.0.0.1:8000/api/login/
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 刷新 Token 接口: http://127.0.0.1:8000/api/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]