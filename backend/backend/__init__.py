# backend/backend/__init__.py

# 引入 celery 实例，确保 Django 启动时共享这个 app
from .celery import app as celery_app

__all__ = ('celery_app',)