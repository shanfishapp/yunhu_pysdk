from typing import ClassVar, Optional
from .logger import logger

class sdk:
    _token: ClassVar[Optional[str]] = None
    _initialized: ClassVar[bool] = False

    @classmethod
    def init(cls, token: str) -> None:
        if cls._initialized:
            logger.error("Token无法重复初始化")
            return

        if not isinstance(token, str) or not token.strip():
            logger.error("无效的Token")
            return

        cls._token = token
        cls._initialized = True
        logger.info("Token初始化成功")

    @classmethod
    def get(cls) -> Optional[str]:
        if cls._token:
            return cls._token
        else:
            logger.error("Token尚未初始化")
            return None