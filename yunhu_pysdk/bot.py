import aiohttp
from aiohttp import web
import asyncio
import logging
from .api import Send
from .sdk import sdk
from .logger import logger


class BOT:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.handlers = []
        self.send = Send()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None

        token = sdk.get()
        if not token:
            raise RuntimeError("Token未初始化，请先调用 sdk.init(token)")
        self.send.init(token)

        self.app.router.add_post("/webhook", self.webhook_handler)

    def add(self, handler):
        self.handlers.append(handler)

    async def webhook_handler(self, request: web.Request):
        try:
            event_json = await request.json()
            logger.info(f"收到 Webhook 消息")

            # 异步分发事件
            asyncio.create_task(self._dispatch_event(event_json))

            return web.json_response({"code": 0, "message": "ok"})
        except Exception as e:
            logger.error(f"Webhook处理失败: {e}")
            return web.json_response({"code": -1, "message": str(e)}, status=500)

    async def _dispatch_event(self, event_json: dict):
        for handler in self.handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_json)
                else:
                    handler(event_json)
            except Exception as e:
                logger.error(f"事件处理器执行失败: {e}")

    async def start(self):
        if self.runner is not None:
            logger.warning("机器人服务已在运行中")
            return

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"机器人已启动，监听地址: http://{self.host}:{self.port}/webhook")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
            self.site = None
            logger.info("机器人服务已关闭")