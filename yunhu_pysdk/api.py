import aiohttp
import asyncio
import urllib.parse
from typing import Dict, Optional, Any
from .logger import logger

class AsyncHTTPClient:
    def __init__(self, timeout=30, headers=None):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.default_headers = headers or {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.default_headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def request(self, method, url, **kwargs):
        try:
            async with self.session.request(method, url, **kwargs) as resp:
                resp.raise_for_status()
                content_type = resp.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return await resp.json()
                elif 'text/' in content_type:
                    return await resp.text()
                else:
                    return await resp.read()
        except Exception as e:
            logger.error(f"HTTP请求失败: {e}")
            return None

    async def get(self, url, **kwargs): return await self.request('GET', url, **kwargs)
    async def post(self, url, **kwargs): return await self.request('POST', url, **kwargs)

async def api_error(title: str, msg: str, exc_info: Optional[Exception] = None):
    error_msg = f"HTTP API {title} 调用错误：{msg}"
    if exc_info:
        error_msg += f" (异常: {str(exc_info)})"
    logger.error(error_msg)

class ResponseWrapper:
    def __init__(self, response_data: Dict[str, Any]):
        self._data = response_data or {}

    def __getattr__(self, name: str) -> Any:
        return self._data.get(name)

    def __repr__(self):
        return f"<ResponseWrapper data={self._data}>"

class Send:
    def __init__(self):
        self.token = None
        self._base_url = "https://chat-go.jwzhd.com/open-apis/v1/bot/"

    def init(self, token: str):
        if not token or not isinstance(token, str):
            raise ValueError("无效Token")
        self.token = token.strip()

    def _build_url(self, endpoint: str):
        encoded_token = urllib.parse.quote(self.token)
        return f"{self._base_url}{endpoint}?token={encoded_token}"

    async def send_message(self, recvId, recvType, msg_type, msg, button=None, parentId=None, batch=False):
        if not self.token:
            logger.error("Token未初始化")
            return None

        endpoint = "batch_send" if batch and isinstance(recvId, list) else "send"
        url = self._build_url(endpoint)

        content_key_map = {
            "image": "imageKey",
            "video": "videoKey",
            "file": "fileKey",
            "markdown": "text",
            "text": "text",
            "html": "text"
        }

        if msg_type not in content_key_map:
            logger.error(f"不支持的消息类型: {msg_type}")
            return None

        content_key = content_key_map[msg_type]
        payload = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": msg_type,
            "content": {content_key: msg}
        }

        if button:
            payload["content"]["button"] = button
        if parentId:
            payload["parentId"] = parentId

        async with AsyncHTTPClient() as client:
            raw_response = await client.post(url, json=payload)
            return ResponseWrapper(raw_response) if raw_response else None

    async def text(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "text", msg, button, parentId, batch)

    async def html(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "html", msg, button, parentId, batch)

    async def markdown(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "markdown", msg, button, parentId, batch)

    async def md(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.markdown(recvId, recvType, msg, button, parentId, batch)

    async def file(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "file", msg, button, parentId, batch)

    async def video(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "video", msg, button, parentId, batch)

    async def image(self, recvId, recvType, msg, button=None, parentId=None, batch=False):
        return await self.send_message(recvId, recvType, "image", msg, button, parentId, batch)