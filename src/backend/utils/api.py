"""
API Utilities

提供 API 请求相关的工具函数。
"""
import httpx
from typing import Optional, Dict, Any
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP 方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class APIClient:
    """通用 API 客户端

    基于 httpx 封装的异步 HTTP 客户端。
    """

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ):
        """初始化 API 客户端

        Args:
            base_url: 基础 URL
            headers: 默认请求头
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers or {}
        self.timeout = timeout

    async def request(
        self,
        method: HTTPMethod,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送 HTTP 请求

        Args:
            method: HTTP 方法
            endpoint: 端点路径（相对或绝对）
            params: URL 查询参数
            data: 表单数据
            json: JSON 数据
            headers: 额外的请求头
            token: Bearer Token

        Returns:
            响应 JSON 数据

        Raises:
            httpx.HTTPError: 请求失败
        """
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"

        request_headers = {**self.default_headers}
        if headers:
            request_headers.update(headers)
        if token:
            request_headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method.value,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers
            )
            response.raise_for_status()
            return response.json()

    async def get(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送 GET 请求"""
        return await self.request(
            HTTPMethod.GET,
            endpoint,
            params=params,
            headers=headers,
            token=token
        )

    async def post(
        self,
        endpoint: str = "",
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送 POST 请求"""
        return await self.request(
            HTTPMethod.POST,
            endpoint,
            data=data,
            json=json,
            headers=headers,
            token=token
        )

    async def put(
        self,
        endpoint: str = "",
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送 PUT 请求"""
        return await self.request(
            HTTPMethod.PUT,
            endpoint,
            data=data,
            json=json,
            headers=headers,
            token=token
        )

    async def delete(
        self,
        endpoint: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """发送 DELETE 请求"""
        return await self.request(
            HTTPMethod.DELETE,
            endpoint,
            params=params,
            headers=headers,
            token=token
        )
