# backend/backend/celery.py

import os
from celery import Celery

# 设置 Django 的默认设置模块环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建一个名为 backend 的 Celery 实例
app = Celery('backend')

# 从 Django 的 settings.py 中加载配置，使用 CELERY_ 作为前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的 Django app 中发现 tasks.py 任务文件
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')