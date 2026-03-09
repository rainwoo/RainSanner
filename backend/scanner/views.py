from rest_framework import generics, viewsets
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Asset, ScanTask, Vulnerability, SniffTask
from .serializers import RegisterSerializer, AssetSerializer, ScanTaskSerializer, VulnerabilitySerializer, SniffTaskSerializer
import subprocess
import json
import os
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import run_nuclei_scan_task, run_nmap_sniff_task, run_nmap_port_scan_task
from django.db.models import Count
from collections import Counter
import csv
from django.http import HttpResponse
from openai import OpenAI


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
    
    @action(detail=False, methods=['post'])
    def sniff(self, request):
        network = request.data.get('network')
        if not network:
            return Response({"error": "必须提供 network (网段) 参数"}, status=400)
            
        # 1. 创建嗅探任务记录
        from .models import SniffTask
        task = SniffTask.objects.create(
            user=request.user,
            network=network,
            status='pending'
        )
        
        # 2. 现在我们把任务 ID 传给后台，而不是直接传网段
        run_nmap_sniff_task.delay(task.id)
        
        return Response({
            "message": f"正在后台全速嗅探 {network}，请在下方列表查看进度！"
        })
    
    @action(detail=True, methods=['post'])
    def port_scan(self, request, pk=None):
        """
        触发主机端口扫描任务
        路由自动生成为: POST /api/assets/{id}/port_scan/
        """
        asset = self.get_object()
        
        # 1. 创建扫描任务，标记扫描类型为 port_service
        task = ScanTask.objects.create(
            asset=asset,
            scan_type='port_service',
            status='pending'
        )
        
        # 2. 扔给 Celery 异步执行
        run_nmap_port_scan_task.delay(task.id)
        
        return Response({
            "message": "主机端口扫描任务已提交后台执行！您可以稍后查看漏洞报告。", 
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
    
    # --- 新增：导出报告功能 ---
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出漏洞报告为 CSV 文件"""
        # 复用上面的 get_queryset 获取当前用户的漏洞数据
        queryset = self.get_queryset()
        
        # 准备 HTTP 响应，明确告诉浏览器这是个 CSV 文件
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="vulnerability_report.csv"'
        
        # 极其关键的一步：写入 UTF-8 BOM 头部！
        # 否则国内用户用微软 Excel 打开 CSV 时，中文会变成一堆乱码
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        # 1. 写入表头
        writer.writerow(['任务ID', '资产名称', '目标地址', '漏洞名称', '危险等级', '发现时间', '修复建议'])
        
        # 危险等级中文化映射
        severity_map = {
            'critical': '严重', 'high': '高危', 'medium': '中危', 
            'low': '低危', 'info': '信息', 'unknown': '未知'
        }
        
        # 2. 逐行写入漏洞数据
        for vuln in queryset:
            severity_zh = severity_map.get(vuln.severity, vuln.severity)
            # 跨表获取资产名称和目标（因为外键关联，可以直接 vuln.task.asset 访问）
            writer.writerow([
                vuln.task.id,
                vuln.task.asset.name,
                vuln.task.asset.target,
                vuln.vuln_name,
                severity_zh,
                vuln.discovered_at.strftime('%Y-%m-%d %H:%M:%S') if vuln.discovered_at else '未知',
                vuln.remediation
            ])
            
        return response
    
class DashboardView(APIView):
    """
    系统首页数据统计看板接口
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. 顶部基础卡片数据统计
        asset_count = Asset.objects.filter(owner=user).count()
        task_count = ScanTask.objects.filter(asset__owner=user).count()
        
        # 【修复】：加上 .order_by() 清除默认时间排序，让 distinct 真正生效
        vuln_count = Vulnerability.objects.filter(task__asset__owner=user)\
            .exclude(severity='info')\
            .values('task__asset_id', 'vuln_name')\
            .order_by()\
            .distinct()\
            .count()

        # 2. 图表数据：按危险等级统计漏洞数量
        # 【修复】：同样加上 .order_by()
        unique_vulns = Vulnerability.objects.filter(task__asset__owner=user)\
            .values('task__asset_id', 'vuln_name', 'severity')\
            .order_by()\
            .distinct()
        
        severity_counter = Counter(item['severity'] for item in unique_vulns)
        severity_stats = [{'severity': k, 'count': v} for k, v in severity_counter.items()]
        
        # 3. 图表数据：按类型统计资产数量
        asset_type_stats = Asset.objects.filter(owner=user)\
            .values('asset_type').annotate(count=Count('asset_type'))

        return Response({
            'counts': {
                'assets': asset_count,
                'tasks': task_count,
                'vulns': vuln_count
            },
            'charts': {
                'severity': severity_stats, 
                'asset_types': list(asset_type_stats)
            }
        })
    
class AiChatView(APIView):
    """
    AI 安全专家答疑接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "问题不能为空"}, status=400)

        # ==========================================
        # ⚠️ 请在这里填入你申请到的免费 API Key
        # ==========================================
        # 这里以 DeepSeek 为例，如果你用其他平台，替换 key 和 base_url 即可
        API_KEY = "sk-902c0a95f6484b35a991727415f47dda" 
        BASE_URL = "https://api.deepseek.com"
        MODEL_NAME = "deepseek-chat"
        
        # 如果你使用 SiliconFlow (完全免费的 Qwen2.5-7B 模型):
        # API_KEY = "你的 SiliconFlow Token"
        # BASE_URL = "https://api.siliconflow.cn/v1"
        # MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

        try:
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            
            # 向 AI 发送请求
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    # System Prompt: 给 AI 赋予安全专家的“人设”
                    {"role": "system", "content": "你是一个资深的 Web 安全专家和白帽子黑客。请用专业、简洁、易懂的中文，回答用户关于漏洞原理、修复代码（如 Java, Python, PHP 等）和渗透测试的问题。如果用户给出了具体的漏洞描述，请直接给出修复方案。"},
                    # User Prompt: 用户实际提问的内容
                    {"role": "user", "content": user_message}
                ],
                stream = False, # 不需要流式输出，等 AI 思考完再一次性返回
                # max_tokens=2048, # 限制回答长度
                # temperature=0.7  # 稍微带点发散性思维
            )
            
            ai_reply = response.choices[0].message.content
            return Response({"reply": ai_reply})
            
        except Exception as e:
            return Response({"error": f"AI 思考时大脑短路了: {str(e)}"}, status=500)
        
class SniffTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """前端获取嗅探历史列表的接口"""
    serializer_class = SniffTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SniffTask.objects.filter(user=self.request.user)
    
class UserProfileView(APIView):
    """
    获取当前登录用户信息与修改密码接口
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 返回当前用户的用户名
        return Response({"username": request.user.username})

    def put(self, request):
        # 处理修改密码逻辑
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"error": "参数不完整"}, status=400)

        # 验证原密码是否正确
        if not user.check_password(old_password):
            return Response({"error": "原密码不正确"}, status=400)

        # 设置新密码并保存
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "密码修改成功，请重新登录"})