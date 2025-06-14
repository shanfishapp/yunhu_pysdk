# http.py
import aiohttp
from typing import Optional, Dict, Any, Union
import json
from .logger import Logger

logger = Logger()

class AsyncHTTPClient:
    """异步HTTP客户端"""
    def __init__(self, timeout=30, headers=None, raise_for_status=True):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.default_headers = headers or {}
        self.raise_for_status = raise_for_status
        self._session = None

    async def __aenter__(self): await self.start(); return self
    async def __aexit__(self, *exc): await self.close()

    async def start(self):
        """启动会话"""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.default_headers,
                raise_for_status=self.raise_for_status
            )

    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, method, url, **kwargs):
        """发送请求"""
        await self.start()
        async with self._session.request(method, url, **kwargs) as resp:
            if self.raise_for_status: resp.raise_for_status()
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type: return await resp.json()
            if 'text/' in content_type: return await resp.text()
            return await resp.read()

    async def get(self, url, **kwargs): return await self.request('GET', url, **kwargs)
    async def post(self, url, **kwargs): return await self.request('POST', url, **kwargs)
    async def put(self, url, **kwargs): return await self.request('PUT', url, **kwargs)
    async def delete(self, url, **kwargs): return await self.request('DELETE', url, **kwargs)
    async def patch(self, url, **kwargs): return await self.request('PATCH', url, **kwargs)

# 全局客户端
_default_client = AsyncHTTPClient()

async def request(method, url, **kwargs): return await _default_client.request(method, url, **kwargs)
async def get(url, **kwargs): return await _default_client.get(url, **kwargs)
async def post(url, **kwargs): return await _default_client.post(url, **kwargs)
async def put(url, **kwargs): return await _default_client.put(url, **kwargs)
async def delete(url, **kwargs): return await _default_client.delete(url, **kwargs)
async def patch(url, **kwargs): return await _default_client.patch(url, **kwargs)

async def init_client(**kwargs): global _default_client; _default_client = AsyncHTTPClient(**kwargs)
async def close_client(): await _default_client.close()
