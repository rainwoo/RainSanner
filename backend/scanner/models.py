# backend/scanner/models.py
from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    """
    资产清单表
    """
    ASSET_TYPE_CHOICES = (
        ('web', 'Web应用'),
        ('host', '主机/服务器'),
    )
    OS_CHOICES = (
        ('windows', 'Windows'),
        ('linux', 'Linux'),
        ('unknown', '未知'),
    )
    
    name = models.CharField(max_length=100, verbose_name="资产名称", help_text="例如：公司官网")
    target = models.CharField(max_length=255, verbose_name="目标地址", help_text="IP地址或URL")
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, verbose_name="资产类型")
    os_type = models.CharField(max_length=20, choices=OS_CHOICES, default='unknown', verbose_name="系统类型")
    # 关联到系统自带的 User 表，表示这个资产是谁添加的。如果用户被删，资产也级联删除
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="所属用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'scanner_asset'
        ordering = ['-created_at'] # 默认按创建时间倒序排列

    def __str__(self):
        return f"{self.name} - {self.target}"


class ScanTask(models.Model):
    """
    扫描任务表
    """
    SCAN_TYPE_CHOICES = (
        ('web_vuln', 'Web漏洞扫描'),
        ('port_service', '端口与服务扫描'),
    )
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '扫描中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    )

    # 关联资产表，表明扫描的是哪个资产
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name="目标资产")
    scan_type = models.CharField(max_length=50, choices=SCAN_TYPE_CHOICES, verbose_name="扫描类型")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="任务状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    class Meta:
        db_table = 'scanner_task'
        ordering = ['-created_at']

    def __str__(self):
        return f"Task:{self.id} - {self.asset.name} - {self.get_status_display()}"


class Vulnerability(models.Model):
    """
    漏洞结果表（用于生成报告）
    """
    SEVERITY_CHOICES = (
        ('critical', '严重'),
        ('high', '高危'),
        ('medium', '中危'),
        ('low', '低危'),
        ('info', '信息'),
    )

    # 关联具体的扫描任务
    task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, verbose_name="所属扫描任务")
    vuln_name = models.CharField(max_length=255, verbose_name="漏洞名称")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="危险等级")
    description = models.TextField(verbose_name="漏洞描述", blank=True, null=True)
    remediation = models.TextField(verbose_name="修复建议", blank=True, null=True)
    matched_at = models.TextField(verbose_name="匹配位置/URL", blank=True, null=True)
    extracted_results = models.TextField(verbose_name="提取的证据", blank=True, null=True)
    curl_command = models.TextField(verbose_name="复现命令(Curl)", blank=True, null=True)
    references = models.TextField(verbose_name="参考链接", blank=True, null=True)
    discovered_at = models.DateTimeField(auto_now_add=True, verbose_name="发现时间")

    class Meta:
        db_table = 'scanner_vulnerability'
        ordering = ['-discovered_at']

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.vuln_name}"


class AIChatHistory(models.Model):
    """
    AI 答疑历史记录表
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="提问用户")
    question = models.TextField(verbose_name="用户问题")
    answer = models.TextField(verbose_name="AI回答")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="对话时间")

    class Meta:
        db_table = 'scanner_ai_chat'
        ordering = ['created_at'] # 聊天记录通常按时间正序排列

    def __str__(self):
        return f"Chat by {self.user.username} at {self.created_at}"