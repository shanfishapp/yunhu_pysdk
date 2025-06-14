import asyncio
from typing import Dict, Optional, Any, List
from urllib.parse import quote
from .logger import Logger
from .sdk import sdk
from .request import get, post

logger = Logger()

async def api_error(title: str, msg: str, exc_info: Optional[Exception] = None):
    """增强的错误日志记录"""
    error_msg = f"HTTP API {title} 调用错误：{msg}"
    if exc_info:
        error_msg += f" (异常: {str(exc_info)})"
    await logger.error(error_msg)

class ResponseWrapper:
    """响应数据包装器，支持自定义字段映射"""
    def __init__(self, response_data: Dict[str, Any], field_map: Optional[Dict[str, str]] = None):
        self._data = response_data or {}
        self._field_map = field_map or {}
        self._success = response_data.get("code", 0) == 0  # 假设code为0表示成功
    
    def __getattr__(self, name: str) -> Any:
        try:
            if name in self._field_map:
                path = self._field_map[name]
                return self._get_nested_value(path)
            elif name in self._data:
                return self._data[name]
            elif name == "success":
                return self._success
        except Exception:
            return None
        raise AttributeError(f"'ResponseWrapper' object has no attribute '{name}'")
    
    def _get_nested_value(self, path: str, default: Any = None) -> Any:
        """从嵌套结构中获取值"""
        keys = path.split('.')
        value = self._data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def __repr__(self) -> str:
        return f"<ResponseWrapper success={self._success} data={self._data}>"

class Send:
    def __init__(self):
        self.token = None
        self._initialized = asyncio.Event()
        self._initializing = False
        self._base_url = "https://chat-go.jwzhd.com/open-apis/v1/bot/".strip()  # 确保无多余空格

    async def init(self):
        """初始化token"""
        if self.token is None and not self._initializing:
            self._initializing = True
            try:
                self.token = await sdk.get()
                if not self.token:
                    raise ValueError("获取的token为空")
                self._initialized.set()
            except Exception as e:
                await api_error("初始化", f"获取token失败", e)
                raise
            finally:
                self._initializing = False

    async def ensure_initialized(self):
        """确保token已初始化"""
        if self.token is None and not self._initializing:
            await self.init()
        elif self.token is None:
            await self._initialized.wait()

    async def _make_request(self, endpoint: str, data: Dict) -> Optional[ResponseWrapper]:
        """执行API请求的终极安全方法"""
        if not self.token:
            await api_error("请求", "无效的token")
            return None

        try:
            # 1. 严格清理输入
            endpoint = str(endpoint).strip().lstrip('/')
            base_url = self._base_url.rstrip('/')
            encoded_token = quote(str(self.token).strip())

            # 2. 使用urllib.parse构建绝对URL
            from urllib.parse import urlunparse, ParseResult
            url = urlunparse(ParseResult(
                scheme='https',
                netloc='chat-go.jwzhd.com',
                path=f'/open-apis/v1/bot/{endpoint}',
                query=f'token={encoded_token}',
                params='',
                fragment=''
            ))

            # 3. 强制验证URL结构
            if not all([url.startswith('https://'), '//' not in url[8:], ' ' not in url]):
                raise ValueError(f"URL结构异常: {repr(url)}")
    
            # 4. 调试输出（实际运行时移除）
            await logger.info(f"最终请求URL（调试）: {url}")  # 确认无隐藏字符

            # 5. 执行请求
            raw_response = await post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30  # 添加超时
            )

            return ResponseWrapper(raw_response, {
                "msgId": "data.messageInfo.msgId",
                "code": "code",
                "id": "data.messageInfo.recvId",
                "type": "data.messageInfo.recvType",
                "success": "code"
            }) if raw_response else None

        except Exception as e:
            await api_error("请求", f"API调用失败: URL={repr(getattr(e, 'url', 'N/A'))}", e)
            return None

    async def request(
        self,
        recvId: Any,
        recvType: str,
        msg_type: str,
        msg: str,
        parentId: Optional[str] = None,
        button: Optional[List[Dict]] = None,
        batch: bool = False,
    ) -> Optional[ResponseWrapper]:
        """发送消息"""
        await self.ensure_initialized()

        content_map = {
            "image": "imageKey",
            "video": "videoKey",
            "file": "fileKey",
            "markdown": "text",
            "text": "text",
            "html": "text",
        }
        
        if msg_type not in content_map:
            await api_error("发送消息", f"不支持的消息类型: {msg_type}")
            return None
        
        if batch and not isinstance(recvId, list):
            await api_error("发送消息", "批量发送时recvId必须为列表")
            return None

        endpoint = "batch_send" if batch and isinstance(recvId, list) else "send"
        content_key = content_map[msg_type]
        
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": msg_type,
            "content": {content_key: msg}
        }
        
        if button:
            data['content']['button'] = button
        if parentId:
            data['parentId'] = parentId
            
        return await self._make_request(endpoint, data)

    # 快捷方法
    async def text(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "text", msg, parentId, button, batch)

    async def html(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "html", msg, parentId, button, batch)

    async def markdown(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "markdown", msg, parentId, button, batch)
    
    async def md(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        return await self.markdown(recvId, recvType, msg, button, batch, parentId)

    async def file(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "file", msg, parentId, button, batch)

    async def video(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "video", msg, parentId, button, batch)

    async def image(self, recvId, recvType, msg, button=None, batch=False, parentId=None):
        button = button or []
        return await self.request(recvId, recvType, "image", msg, parentId, button, batch)
