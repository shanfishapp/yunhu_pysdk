import asyncio
from typing import Dict, Optional, Any, List
from logger import Logger
from sdk import sdk
from request import get, post

logger = Logger()

async def api_error(title: str, msg: str):
    await logger.error(f"HTTP API {title} 调用错误：{msg}")

class ResponseWrapper:
    """响应数据包装器，支持自定义字段映射"""
    def __init__(self, response_data: Dict[str, Any], field_map: Optional[Dict[str, str]] = None):
        self._data = response_data or {}
        self._field_map = field_map or {}  # 例如 {"msgId": "data.msgId"}
    
    def __getattr__(self, name: str) -> Any:
        # 如果字段在映射表中，按路径解析
        if name in self._field_map:
            path = self._field_map[name]
            return self._get_nested_value(path)
        # 否则直接查找
        elif name in self._data:
            return self._data[name]
        raise AttributeError(f"'ResponseWrapper' object has no attribute '{name}'")
    
    def _get_nested_value(self, path: str, default: Any = None) -> Any:
        """从嵌套结构中获取值，如 'data.msgId'"""
        keys = path.split('.')
        value = self._data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def __repr__(self) -> str:
        return f"<ResponseWrapper {self._data}>"

class Send:
    def __init__(self):
        self.token = None
        self._initializing = False
        self._initialized = asyncio.Event()
        asyncio.create_task(self._initialize_token())

    async def _initialize_token(self):
        try:
            self._initializing = True
            self.token = await sdk.get()
            self._initialized.set()
        except Exception as e:
            await logger.error(f"初始化token失败: {str(e)}")
            raise
        finally:
            self._initializing = False

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
        """发送消息，SDK 内部自动处理字段映射"""
        if self.token is None and not self._initializing:
            await self._initialize_token()
        elif self.token is None:
            await self._initialized.wait()
        
        allow = {
            "image": "imageKey",
            "video": "videoKey",
            "file": "fileKey",
            "markdown": "text",
            "text": "text",
            "html": "text",
        }
        
        if msg_type not in allow:
            await api_error("发送消息", f"不支持的消息类型: {msg_type}")
            return None
        
        key = allow[msg_type]
        
        url = (
            "https://chat-go.jwzhd.com/open-apis/v1/bot/batch_send?token=" + self.token
            if batch and isinstance(recvId, list)
            else "https://chat-go.jwzhd.com/open-apis/v1/bot/send?token=" + self.token
        )
        
        if batch and not isinstance(recvId, list):
            await api_error("发送消息", "recvId必须为有效数组")
            return None
        
        data = {
            "recvId": recvId,
            "recvType": recvType,
            "contentType": msg_type,
            "content": {
                key: msg
            }
        }
        
        if button:
            data['content']['button'] = button
        if parentId:
            data['parentId'] = parentId
            
        try:
            raw_response = await post(url, json=data, headers={"Content-Type": "application/json"})
            
            # 定义字段映射（数组/字典）
            field_map = {
                "msgId": "data.messageInfo.msgId",
                "msg": "msg",
                "code": "code",
                "id": "data.messageInfo.recvId",
                "type": "data.messageInfo.recvType"
            }
            
            return ResponseWrapper(raw_response, field_map)
        except Exception as e:
            await api_error("发送消息", f"请求失败: {str(e)}")
            return None
    async def text(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "text", msg, parentId, button, batch)
    async def html(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "html", msg, parentId, button, batch)
    async def md(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "markdown", msg, parentId, button, batch)
    async def markdown(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "markdown", msg, parentId, button, batch)
    async def file(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "file", msg, parentId, button, batch)
    async def video(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "video", msg, parentId, button, batch)
    async def image(self, recvId, recvType, msg, button=[], batch=False, parentId=None):
        return await self.request(recvId, recvType, "image", msg, parentId, button, batch)
        
class Edit:
    def __init__(self):
        self.token = None
        self._initializing = False
        self._initialized = asyncio.Event()
        asyncio.create_task(self._initialize_token())

    async def _initialize_token(self):
        try:
            self._initializing = True
            self.token = await sdk.get()
            self._initialized.set()
        except Exception as e:
            await logger.error(f"初始化token失败: {str(e)}")
            raise
        finally:
            self._initializing = False
    async def request(recvId, recvType, type, msg, msgId, button=[])