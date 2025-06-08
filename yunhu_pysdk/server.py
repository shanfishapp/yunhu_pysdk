from quart import Quart, request, jsonify
import asyncio
import threading
from typing import Callable, Dict, Any, List, Optional, Awaitable, Union
from yunhu_pysdk.logger import Logger

logger = Logger()

class DictWithAttr(dict):
    """支持属性访问的字典（兼容 .key 和 ['key'] 写法）"""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"没有这个属性: {key}")
    
    def __setattr__(self, key, value):
        self[key] = value

class alias:
    """数据别名描述符（从存储的data中解析嵌套值）"""
    def __init__(self, path: Union[str, List[str]]):
        self.path = path.split('.') if isinstance(path, str) else path
    
    def __get__(self, obj, owner):
        if obj is None:
            return self
        if obj._data is None:
            return None
        
        value = obj._data
        try:
            for key in self.path:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

class Webhook:
    """直接使用的Webhook服务（支持add()和run()）"""
    # 基础字段别名
    event = alias("header.eventType")
    msgtype = alias("event.message.contentType")
    cmd = alias("event.message.commandName")
    cmdid = alias("event.message.commandId")
    level = alias("event.sender.senderUserLevel")
    nick = alias("event.sender.senderNickName")
    user_id = alias("event.sender.senderId")
    @property
    def chat_type(self):
        """动态获取聊天类型"""
        if self._data is None or self.msgtype is None:
            return None
        text_types = ("text", "markdown", "html")
        media_types = ("image", "video", "file")
        if self.msgtype in text_types + media_types:
            return "chat"
        return "group" if self.msgtype == "form" else None
    
    @property
    def msg(self):
        if self._data is None or self.msgtype is None:
            return None
        try:
            if self.msgtype in ("text", "markdown", "html"):
                return self._data["event"]["message"]["content"]["text"]
            elif self.msgtype in ("image", "video", "file"):
                return self._data["event"]["message"]["content"][f"{self.msgtype}Url"]
            elif self.msgtype == "form":
                return self._data["event"]["message"]["content"]["formJson"]
            return None
        except KeyError:
            return None
    
    @property
    def id(self):
        """动态获取ID（根据chat_type判断来源）"""
        if self._data is None:
            return None
        if self.chat_type == "chat":
            return self._data["event"]["sender"]["senderId"]
        return self._data["event"]["chat"]["chatId"]
    
    @property
    def type(self):
        """动态获取类型（chat_type为bot时返回user）"""
        return "user" if self.chat_type == "chat" else self.chat_type
    
    def __init__(self):
        self.app = Quart(__name__)
        self.callbacks: List[Callable[[DictWithAttr], Awaitable[None]]] = []
        self._data = None
        self.port = None
        self.path = None
    
    def _setup_routes(self):
        if self.path is None:
            logger.error("Webhook路径未设置")
            raise ValueError("Webhook路径未设置")
        
        @self.app.route(self.path, methods=['POST'])
        async def _webhook_handler():
            try:
                json_data = await request.get_json()
                if json_data is None:
                    logger.error("接收到无效的JSON数据")
                    return jsonify({'error': '无效的JSON数据'}), 400
                
                self._data = json_data  
                data = DictWithAttr(json_data)
                
                data.event = self.event
                data.id = self.id
                data.type = self.type
                data.chat_type = self.chat_type
                data.msg = self.msg
                data.cmd = self.cmd
                data.cmdid = self.cmdid
                data.msgtype = self.msgtype
                data.level = self.level
                data.nick = self.nick
                data.user_id = self.user_id
                
                logger.debug(f"接收到Webhook数据: {data}")
                
                # 异步执行所有回调
                await asyncio.gather(*[callback(data) for callback in self.callbacks])
                
                logger.info("Webhook处理成功")
                return jsonify({'status': 'success'}), 200
            except Exception as e:
                logger.error(f"处理Webhook时出错: {str(e)}", exc_info=True)
                return jsonify({'error': str(e)}), 500
    
    def add(self, callback: Callable[[DictWithAttr], Awaitable[None]]):
        """添加异步回调函数"""
        if not callable(callback):
            logger.error("回调必须是一个可调用函数")
            raise ValueError("回调必须是一个可调用函数")
        if not asyncio.iscoroutinefunction(callback):
            logger.error("回调必须是异步函数")
            raise TypeError("回调必须是异步函数")
        self.callbacks.append(callback)
        logger.info(f"已添加新回调函数: {callback.__name__}")
    
    def run(self, port: int = 5000, path: str = '/webhook'):
        """直接启动Webhook服务器（阻塞当前线程）"""
        self.port = port
        self.path = path
        self._setup_routes()
        logger.info(f"Webhook服务已启动 → 端口: {port}, 路径: {path}")
        asyncio.run(self.app.run_task(host="0.0.0.0", port=port))
    
    def run_in_thread(self, port: int = 5000, path: str = '/webhook'):
        """在后台线程中启动Webhook服务器（非阻塞）"""
        self.port = port
        self.path = path
        self._setup_routes()
        
        async def run_server():
            await self.app.run_task(host="0.0.0.0", port=port)
        
        def thread_target():
            logger.info(f"正在后台线程启动Webhook服务，监听端口: {port}")
            asyncio.run(run_server())
        
        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()
        logger.info("Webhook后台服务线程已启动")
        return thread