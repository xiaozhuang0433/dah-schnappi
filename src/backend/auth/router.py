"""
Authentication Router

认证相关的 API 路由。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from src.infrastructure.database import db, UserInDB, UserCreate, UserResponse, UserLogin
from src.infrastructure.cache import cache
from src.auth.security import verify_password, get_password_hash, create_access_token
from src.auth.dependencies import get_current_user, get_current_user_id
from src.utils.crypto import get_crypto
from src.utils.logger import get_logger
from typing import Dict, Any


router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> UserResponse:
    """用户注册

    Args:
        user_data: 用户注册数据

    Returns:
        创建的用户信息

    Raises:
        HTTPException: 如果用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    if await db.exists(UserInDB, "username", user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 检查邮箱是否已存在
    if await db.exists(UserInDB, "email", user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 创建用户
    user_id = await db.insert(UserInDB, {
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password)
    })

    user = await db.get_by_id(UserInDB, user_id)

    logger.info(f"New user registered: {user.username} (ID: {user.id})")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/login")
async def login(login_data: UserLogin) -> Dict[str, Any]:
    """用户登录

    Args:
        login_data: 登录数据

    Returns:
        包含 access_token 和用户信息的字典

    Raises:
        HTTPException: 如果用户名或密码错误
    """
    # 查找用户
    user = await db.get_one_by_field(UserInDB, "username", login_data.username)

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问 Token
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

    logger.info(f"User logged in: {user.username} (ID: {user.id})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
) -> UserResponse:
    """获取当前用户信息

    Args:
        current_user: 当前用户（通过依赖注入）

    Returns:
        当前用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/logout")
async def logout(
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, str]:
    """用户登出

    注意：由于使用无状态 JWT，登出主要通过客户端删除 Token 实现。
    此接口主要用于：
    1. 记录登出日志
    2. 可选：将 Token 加入黑名单（使用缓存）

    Args:
        current_user_id: 当前用户 ID

    Returns:
        成功消息
    """
    # 如果需要，可以将当前 Token 加入黑名单
    # 这里简化处理，只记录日志
    logger.info(f"User logged out: ID {current_user_id}")

    return {"message": "Successfully logged out"}
