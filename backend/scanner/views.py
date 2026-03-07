from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Asset, ScanTask, Vulnerability
from .serializers import RegisterSerializer, AssetSerializer, ScanTaskSerializer, VulnerabilitySerializer
import subprocess
import json
import os
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import run_nuclei_scan_task

class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    """
    queryset = User.objects.all()
    # 允许任何人访问这个接口（因为注册时用户还没有 Token）
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return Asset.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # === 以下为新增的扫描接口逻辑 ===
    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
            """
            触发异步扫描任务
            """
            asset = self.get_object()
            # 提取前端传来的扫描模式，默认为 'quick' (快速扫描)
            mode = request.data.get('mode', 'quick')
            
            # 1. 在数据库中创建一个状态为 pending 的任务记录
            task = ScanTask.objects.create(
                asset=asset,
                scan_type='web_vuln',
                status='pending'
            )
            
            # 2. 核心魔法：使用 .delay() 将任务扔给 Celery + Redis！
            # 这里只传递 task.id 过去，不要传递整个对象
            run_nuclei_scan_task.delay(task.id, mode)
            
            # 3. 瞬间返回给前端，前端再也不会超时了！
            return Response({
                        "message": f"[{'快速' if mode == 'quick' else '深度'}扫描] 任务已提交后台执行！", 
                        "task_id": task.id
                    })
    
class ScanTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    扫描任务查看接口
    """
    serializer_class = ScanTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 权限控制：只能看属于自己资产的扫描任务
        # asset__owner 表示跨越 asset 表查询 owner 字段
        return ScanTask.objects.filter(asset__owner=self.request.user)


class VulnerabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    漏洞结果查看接口
    """
    serializer_class = VulnerabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 权限控制：只能看属于自己资产的漏洞
        queryset = Vulnerability.objects.filter(task__asset__owner=self.request.user)
        
        # 支持前端通过 ?task=ID 来过滤特定任务的漏洞
        task_id = self.request.query_params.get('task')
        if task_id is not None:
            queryset = queryset.filter(task_id=task_id)
            
        return queryset