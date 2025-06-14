# http.py
import aiohttp
from typing import Optional, Dict, Any, Union
import json
import logging

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """
    异步HTTP客户端，基于aiohttp封装
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        raise_for_status: bool = True,
        json_serialize: callable = json.dumps,
        json_deserialize: callable = json.loads,
    ):
        """
        初始化HTTP客户端
        
        :param base_url: 基础URL，所有请求都会基于这个URL
        :param timeout: 请求超时时间(秒)
        :param headers: 默认请求头
        :param raise_for_status: 是否在响应状态码非200时抛出异常
        :param json_serialize: JSON序列化方法
        :param json_deserialize: JSON反序列化方法
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.default_headers = headers or {}
        self.raise_for_status = raise_for_status
        self.json_serialize = json_serialize
        self.json_deserialize = json_deserialize
        self._session = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def start(self):
        """启动客户端会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.default_headers,
                json_serialize=self.json_serialize,
            )

    async def close(self):
        """关闭客户端会话"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        发送HTTP请求
        
        :param method: HTTP方法 (GET, POST, PUT, DELETE等)
        :param url: 请求URL
        :param params: 查询参数
        :param data: 请求体数据 (字典、字符串或字节)
        :param json: JSON可序列化数据
        :param headers: 请求头
        :param cookies: cookies
        :param allow_redirects: 是否允许重定向
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据 (自动根据Content-Type处理)
        :raises: aiohttp.ClientError 如果请求失败
        """
        if not self._session or self._session.closed:
            await self.start()

        request_headers = {**self.default_headers, **(headers or {})}
        
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                cookies=cookies,
                allow_redirects=allow_redirects,
                **kwargs
            ) as response:
                if self.raise_for_status:
                    response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                
                if "application/json" in content_type:
                    return await response.json(loads=self.json_deserialize)
                elif "text/" in content_type:
                    return await response.text()
                else:
                    return await response.read()
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP请求失败: {method} {url} - {str(e)}")
            raise

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        GET请求
        
        :param url: 请求URL
        :param params: 查询参数
        :param headers: 请求头
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据
        """
        return await self.request("GET", url, params=params, headers=headers, **kwargs)

    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        POST请求
        
        :param url: 请求URL
        :param data: 请求体数据
        :param json: JSON可序列化数据
        :param headers: 请求头
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据
        """
        return await self.request("POST", url, data=data, json=json, headers=headers, **kwargs)

    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        PUT请求
        
        :param url: 请求URL
        :param data: 请求体数据
        :param json: JSON可序列化数据
        :param headers: 请求头
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据
        """
        return await self.request("PUT", url, data=data, json=json, headers=headers, **kwargs)

    async def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        DELETE请求
        
        :param url: 请求URL
        :param params: 查询参数
        :param headers: 请求头
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据
        """
        return await self.request("DELETE", url, params=params, headers=headers, **kwargs)

    async def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict[str, Any], str, bytes]:
        """
        PATCH请求
        
        :param url: 请求URL
        :param data: 请求体数据
        :param json: JSON可序列化数据
        :param headers: 请求头
        :param kwargs: 其他aiohttp请求参数
        :return: 响应数据
        """
        return await self.request("PATCH", url, data=data, json=json, headers=headers, **kwargs)


# 全局默认客户端实例
_default_client = AsyncHTTPClient()


async def request(
    method: str,
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送请求"""
    return await _default_client.request(method, url, **kwargs)


async def get(
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送GET请求"""
    return await _default_client.get(url, **kwargs)


async def post(
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送POST请求"""
    return await _default_client.post(url, **kwargs)


async def put(
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送PUT请求"""
    return await _default_client.put(url, **kwargs)


async def delete(
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送DELETE请求"""
    return await _default_client.delete(url, **kwargs)


async def patch(
    url: str,
    **kwargs
) -> Union[Dict[str, Any], str, bytes]:
    """使用默认客户端发送PATCH请求"""
    return await _default_client.patch(url, **kwargs)


async def init_client(**kwargs):
    """初始化默认客户端"""
    global _default_client
    _default_client = AsyncHTTPClient(**kwargs)


async def close_client():
    """关闭默认客户端"""
    await _default_client.close()
