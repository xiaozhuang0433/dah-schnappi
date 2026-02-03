"""
API Package

导出所有 API 路由模块。
"""
from .config import router as config_router
from .chat import router as chat_router
from .health import router as health_router

__all__ = [
    "config_router",
    "chat_router",
    "health_router"
]
