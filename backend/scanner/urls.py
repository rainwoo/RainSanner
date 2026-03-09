from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, AssetViewSet, ScanTaskViewSet, VulnerabilityViewSet, DashboardView, AiChatView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 使用 DefaultRouter 自动生成 RESTful 风格的路由
router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset') 
# 这样会自动生成 /api/assets/ (GET/POST) 和 /api/assets/<id>/ (GET/PUT/DELETE)
# 注册任务和漏洞的路由
router.register(r'tasks', ScanTaskViewSet, basename='task')
router.register(r'vulnerabilities', VulnerabilityViewSet, basename='vulnerability')

urlpatterns = [
    # 注册接口: http://127.0.0.1:8000/api/register/
    path('register/', RegisterView.as_view(), name='auth_register'),
    
    # 登录接口 (获取 Token): http://127.0.0.1:8000/api/login/
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # 刷新 Token 接口: http://127.0.0.1:8000/api/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- 首页大盘接口 ---
    path('dashboard/stats/', DashboardView.as_view(), name='dashboard_stats'),

    # --- 新增 AI 对话接口 ---
    path('ai/ask/', AiChatView.as_view(), name='ai_ask'),

    # 将 router 自动生成的路由包含进来
    path('', include(router.urls)),
]