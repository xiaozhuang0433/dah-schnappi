"""
Authentication Dependencies

FastAPI 依赖项，用于保护需要认证的路由。
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from infrastructure.database import db, UserInDB
from .security import decode_access_token


# HTTP Bearer 安全方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """获取当前登录用户

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        当前用户对象

    Raises:
        HTTPException: 如果 Token 无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await db.get_by_id(UserInDB, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_id(
    current_user: UserInDB = Depends(get_current_user)
) -> int:
    """获取当前用户 ID

    这是一个简化的依赖项，用于只需要 user_id 的场景。

    Args:
        current_user: 当前用户对象

    Returns:
        用户 ID
    """
    return current_user.id


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserInDB]:
    """可选的认证依赖

    如果提供了 Token 则验证，否则返回 None。
    用于某些可以匿名访问但登录后有额外功能的端点。

    Args:
        credentials: HTTP Bearer credentials（可选）

    Returns:
        用户对象或 None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
