"""
FastAPI Main Application

工作日志系统的主应用程序入口。
"""
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from infrastructure.database import db
from infrastructure.cache import cache
from utils.logger import setup_logger, get_logger
from auth.router import router as auth_router
from api.config import router as config_router
from api.chat import router as chat_router
from api.health import router as health_router


# 设置日志
setup_logger(
    name="worklog",
    level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    启动时初始化数据库和缓存，关闭时清理资源。
    """
    # 启动
    logger.info("Starting Work Log System...")
    logger.info(f"Database implementation: {settings.DATABASE_IMPLEMENTATION}")
    logger.info(f"Cache implementation: {settings.CACHE_IMPLEMENTATION}")

    try:
        # 连接数据库
        db.connect()
        logger.info("Database connected successfully")

        # 预热缓存
        logger.info("Cache initialized")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

    yield

    # 关闭
    logger.info("Shutting down Work Log System...")
    try:
        db.disconnect()
        cache.clear()
        logger.info("Resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered work log system with Git integration",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册路由
app.include_router(auth_router)
app.include_router(config_router)
app.include_router(chat_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": settings.DATABASE_IMPLEMENTATION,
        "cache": settings.CACHE_IMPLEMENTATION
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
