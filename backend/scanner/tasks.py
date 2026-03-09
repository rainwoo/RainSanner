# backend/scanner/tasks.py

import subprocess
import json
import os
from celery import shared_task
from .models import ScanTask, Vulnerability, SniffTask
from django.utils import timezone 
import logging
from django.contrib.auth.models import User
from .models import Asset
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

@shared_task
def run_nmap_port_scan_task(task_id):
    """
    异步执行 Nmap 端口与服务扫描任务
    """
    try:
        task = ScanTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        # 定义输出为 XML 格式的文件
        output_file = f"nmap_port_output_{task.id}.xml"
        
        # 构造 Nmap 命令:
        # -sV: 探测开放的端口来决定服务和版本信息
        # -T4: 较快的执行速度
        # -oX: 将结果输出为 XML 格式以便 Python 结构化解析
        command = ["nmap", "-sV", "-T4", task.asset.target, "-oX", output_file]
        
        # 执行命令 (阻塞等待执行完毕)
        subprocess.run(command, capture_output=True, text=True, check=False)
        
        # 解析 XML 结果并存入 Vulnerability 表 (作为 info 级别)
        if os.path.exists(output_file):
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            # 遍历所有的 host 节点
            for host in root.findall('host'):
                ports = host.find('ports')
                if ports is not None:
                    # 遍历每一个 port 节点
                    for port in ports.findall('port'):
                        state = port.find('state').get('state')
                        # 我们只关心处于 "open" (开放) 状态的端口
                        if state == 'open':
                            portid = port.get('portid')
                            protocol = port.get('protocol')
                            
                            service = port.find('service')
                            service_name = service.get('name') if service is not None else 'unknown'
                            product = service.get('product') if service is not None else ''
                            version = service.get('version') if service is not None else ''
                            
                            details = f"协议: {protocol}\n服务: {service_name}\n产品: {product} {version}"
                            
                            # 将开放端口作为一个“信息(info)”级别的漏洞记录存入数据库
                            Vulnerability.objects.create(
                                task=task,
                                vuln_name=f"开放端口: {portid}/{protocol} ({service_name})",
                                severity='info', # 标记为 info 级别
                                description=f"目标主机开放了 {portid} 端口，运行 {service_name} 服务。",
                                extracted_results=details.strip(),
                                remediation="如果是危险或非必要端口（如 445, 3389, 6379, 27017 等），建议通过防火墙限制访问或直接关闭服务。"
                            )
            # 解析完毕，清理临时文件
            os.remove(output_file)
            
        task.status = 'completed'
        task.save()
        return f"Port scan task {task_id} completed successfully."

    except Exception as e:
        task = ScanTask.objects.get(id=task_id)
        task.status = 'failed'
        task.save()
        return f"Port scan task {task_id} failed: {str(e)}"

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
def run_nmap_sniff_task(task_id):
    """
    异步执行 Nmap 主机存活嗅探并探测操作系统，自动入库并更新历史记录
    """
    try:
        # 获取刚才创建的嗅探任务记录
        task = SniffTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        user = task.user
        network_range = task.network
        
        # 构造并执行 Nmap 命令
        command = ["nmap", "-F", "-O", "-T4", network_range, "-oX", "-"]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        added_count = 0
        
        try:
            root = ET.fromstring(result.stdout)
        except ET.ParseError:
            task.status = 'failed'
            task.result = "嗅探失败：Nmap 输出解析错误（请检查运行Celery的终端是否具有管理员/root权限）"
            task.finished_at = timezone.now()
            task.save()
            return task.result
            
        # 遍历主机... (此处解析逻辑与你原代码相同)
        for host in root.findall('host'):
            status = host.find('status')
            if status is not None and status.get('state') == 'up':
                address = host.find('address')
                if address is None:
                    continue
                ip = address.get('addr')
                
                os_type = 'unknown'
                os_el = host.find('os')
                if os_el is not None:
                    osmatch = os_el.find('osmatch')
                    if osmatch is not None:
                        os_name = osmatch.get('name', '').lower()
                        if 'windows' in os_name:
                            os_type = 'windows'
                        elif 'linux' in os_name:
                            os_type = 'linux'
                
                if not Asset.objects.filter(target=ip, owner=user).exists():
                    Asset.objects.create(
                        name=f"自动嗅探主机_{ip}", target=ip, asset_type='host', os_type=os_type, owner=user
                    )
                    added_count += 1
                        
        # 记录成功结果
        task.status = 'completed'
        task.result = f"嗅探完成！成功发现并自动入库了 {added_count} 个存活主机。"
        task.finished_at = timezone.now()
        task.save()
        return task.result

    except Exception as e:
        task = SniffTask.objects.get(id=task_id)
        task.status = 'failed'
        task.result = f"系统异常: {str(e)}"
        task.finished_at = timezone.now()
        task.save()
        return task.result