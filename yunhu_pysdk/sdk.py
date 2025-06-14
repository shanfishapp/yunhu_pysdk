from typing import ClassVar, Optional
import asyncio
from .logger import Logger

logger = Logger()

class sdk:
    _token: ClassVar[Optional[str]] = None
    _initialized: ClassVar[bool] = False

    @classmethod
    async def init(cls, token: str) -> None:
        if cls._initialized:
            await logger.error("Token无法重复初始化", True)
            return
        
        if not isinstance(token, str) or not token.strip():
            await logger.error("无效的Token", True)
            return
        
        cls._token = token
        cls._initialized = True
        await logger.info("Token初始化成功")
    @classmethod
    async def get(cls):
        if cls._token:
            return cls._token
        else:
            await logger.error("Token尚未初始化", True)