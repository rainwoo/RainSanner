# backend/scanner/tasks.py

import subprocess
import json
import os
from celery import shared_task
from .models import ScanTask, Vulnerability
import logging
from django.contrib.auth.models import User
from .models import Asset

logger = logging.getLogger(__name__)

@shared_task
def run_nuclei_scan_task(task_id, mode='quick'):
    """
    异步执行 Nuclei 扫描任务
    """
    try:
        # 获取数据库中的任务对象
        task = ScanTask.objects.get(id=task_id)
        asset = task.asset
        
        # 更新状态为正在运行
        task.status = 'running'
        task.save()

        # 定义输出文件
        output_file = f"nuclei_output_{task.id}.json"
        
        # 构造执行命令
        # 构造执行命令 (加入性能优化参数)
        command = [
            "nuclei", 
            "-target", asset.target, 
            "-j", "-o", output_file,
            # "-silent",
            
            # === 以下为新增的提速优化参数 ===
            
            
            # # 2. 并发与速率限制 (根据你的服务器带宽和目标承受能力调整)
            # "-c", "10",      # 模板并发数 (默认25，我们翻倍到50)
            # "-bs", "50",     # 批量大小 (默认25，翻倍到50)
            # "-rl", "30",    # 每秒最大请求数限制 Rate Limit (默认150，宽带好可设为 300-500)
            

            
            # (可选) 4. 指定扫描特定的技术栈或标签，比如只扫 CVE
            # "-tags", "cve,rce,sqli", 
        ]

        # 根据模式动态添加不同的性能和深度参数
        if mode == 'quick':
            # 【快速扫描】：只扫严重(critical)和高危(high)，高并发，低超时，不重试
            command.extend([
                "-s", "critical,high,medium", 
                "-c", "50", 
                "-timeout", "3",
                "-retries", "0"
            ])
        else:
            # 【深度扫描】：扫严重到低危(low)，包含中危，降低并发求稳，增加超时和重试
            command.extend([
                "-s", "critical,high,medium,low,info", 
                "-c", "20", 
                "-timeout", "10",
                "-retries", "2"
            ])
        
        # 1. 打印即将执行的完整命令！
        logger.warning(f"即将执行的命令: {' '.join(command)}")
        
        # 2. 捕获终端的标准输出和错误
        result = subprocess.run(command, capture_output=True, text=True)
        
        # 3. 打印 Nuclei 的原始输出 (去运行 Celery 的那个终端里看！)
        logger.warning(f"Nuclei 原始输出: {result.stdout}")
        if result.stderr:
            logger.warning(f"Nuclei 错误输出: {result.stderr}")

        # 执行系统命令（此时是在 Celery worker 的后台进程中阻塞，不会影响 Django 主线程）
        subprocess.run(command, check=False)
        
        # 解析结果并存入数据库
        if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                item = json.loads(line)
                                info = item.get('info', {})
                                
                                # 处理可能为列表的字段，将其转换为换行符拼接的字符串
                                extracted = item.get('extracted-results', [])
                                extracted_str = '\n'.join(extracted) if isinstance(extracted, list) else str(extracted or '')
                                
                                refs = info.get('reference', [])
                                refs_str = '\n'.join(refs) if isinstance(refs, list) else str(refs or '')

                                Vulnerability.objects.create(
                                    task=task,
                                    vuln_name=info.get('name', '未知漏洞'),
                                    severity=info.get('severity', 'info'),
                                    description=info.get('description', ''),
                                    remediation=info.get('remediation', ''),
                                    # 存入新增的字段
                                    matched_at=item.get('matched-at', ''),
                                    extracted_results=extracted_str,
                                    curl_command=item.get('curl-command', ''),
                                    references=refs_str
                                )
                    os.remove(output_file) # 清理临时文件
        
        # 扫描成功，更新状态
        task.status = 'completed'
        task.save()
        return f"Task {task_id} completed successfully."

    except Exception as e:
        # 发生异常，记录失败状态
        task = ScanTask.objects.get(id=task_id)
        task.status = 'failed'
        task.save()
        return f"Task {task_id} failed: {str(e)}"


@shared_task
def run_nmap_sniff_task(network_range, user_id):
    """
    异步执行 Nmap 主机存活嗅探，并自动入库
    """
    try:
        user = User.objects.get(id=user_id)
        
        # 构造 Nmap 命令
        # -sn: 只进行 Ping 扫描，不扫描端口 (速度极快)
        # -T4: 设置相对较快的扫描速度
        # -oG -: 将结果以 Grepable (易于程序解析) 的格式输出到控制台
        command = ["nmap", "-sn", "-T4", network_range, "-oG", "-"]
        
        # 执行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        added_count = 0
        
        # 逐行解析 Nmap 的输出
        for line in result.stdout.splitlines():
            # Grepable 格式中，存活主机会包含 "Status: Up"
            if "Status: Up" in line:
                # 典型的输出行: Host: 192.168.1.1 (router.local)  Status: Up
                parts = line.split(" ")
                if len(parts) >= 2:
                    ip = parts[1] # 提取出 IP 地址
                    
                    # 检查当前用户是否已经添加过这个 IP，避免重复添加
                    if not Asset.objects.filter(target=ip, owner=user).exists():
                        Asset.objects.create(
                            name=f"自动嗅探主机_{ip}",
                            target=ip,
                            asset_type='host', # 自动标记为 主机/服务器 类型
                            owner=user
                        )
                        added_count += 1
                        
        return f"网段 {network_range} 嗅探完成，成功发现并添加了 {added_count} 个存活主机。"

    except Exception as e:
        return f"嗅探任务失败: {str(e)}"