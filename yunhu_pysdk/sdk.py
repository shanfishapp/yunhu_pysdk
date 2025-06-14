from typing import ClassVar, Optional

class sdk:
    _token: ClassVar[Optional[str]] = None
    _initialized: ClassVar[bool] = False

    @classmethod
    def init(cls, token: str) -> None:
        if cls._initialized:
            await logger.error("Token无法重复初始化", True)
        if not isinstance(token, str) or not token.strip():
           await logger.error("无效的Token", True)
        cls._token = token
        cls._initialized = True

    @classmethod
    async def get(cls) -> str:
        if cls._token is None:
            await logger.error("Token未设置", True)
        return cls._token

    @classmethod
    def clear(cls) -> None:
        cls._token = None
        cls._initialized = False