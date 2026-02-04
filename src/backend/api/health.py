"""
Health Check API Router

健康检查相关的 API 路由。
"""
from fastapi import APIRouter
from datetime import datetime
from config.settings import settings


router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": settings.DATABASE_IMPLEMENTATION,
            "cache": settings.CACHE_IMPLEMENTATION,
            "llm": settings.LLM_PROVIDER
        }
    }


@router.get("/version")
async def get_version():
    """获取版本信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered work log system with Git integration"
    }
