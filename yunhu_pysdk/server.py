from quart import Quart, request, jsonify
from typing import Callable, Dict, Any, List, Optional, Union, Awaitable
import asyncio
import threading

class DictWithAttr(dict):
    """支持属性访问的字典（同时兼容 .key 和 ['key'] 写法）"""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"No such attribute: {key}")

class alias:
    """数据别名描述符"""
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
    """强制异步的Webhook服务，所有回调必须为async函数"""
    # 基础字段别名
    event = alias("header.eventType")
    msgtype = alias("event.message.contentType")
    cmd = alias("event.message.commandName")
    cmdid = alias("event.message.commandId")
    level = alias("event.sender.senderUserLevel")
    nick = alias("event.sender.senderNickName")
    
    @property
    def chat_type(self):
        """动态获取聊天类型"""
        return alias("event.chat.chatType").__get__(self, AsyncWebhook)
    
    @property
    def msg(self):
        if self.msgtype == "text" or self.msgtype == "markdown" or self.msgtype == "html":
            return alias("event.message.content.text").__get__(self, AsyncWebhook)
        elif self.msgtype == "image" or self.msgtype == "video" or self.msgtype == "file":
            return alias(f"event.message.content.{self.msgtype}Url").__get__(self, AsyncWebhook)
        elif self.msgtype == "form":
            return alias(f"event.message.content.formJson").__get__(self, AsyncWebhook)
            
    @property
    def id(self):
        """动态获取ID（根据chat_type判断来源）"""
        if self.chat_type == "bot":
            return alias("event.sender.senderId").__get__(self, AsyncWebhook)
        return alias("event.chat.chatId").__get__(self, AsyncWebhook)
    
    @property
    def type(self):
        """动态获取类型（chat_type为bot时返回user）"""
        return "user" if self.chat_type == "bot" else self.chat_type
    
    def __init__(self):
        self.app = Quart(__name__)
        self.callbacks: List[Callable[[DictWithAttr], Awaitable[None]]] = []
        self._data = None
        self.port = None
        self.path = None
    
    def _setup_routes(self):
        if self.path is None:
            raise ValueError("Webhook path not set")
        
        @self.app.route(self.path, methods=['POST'])
        async def _webhook_handler():
            try:
                json_data = await request.get_json()
                if json_data is None:
                    return jsonify({'error': 'Invalid JSON data'}), 400
                
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
                
                data.MESSAGE == "message.receive.normal"
                data.SETTING == "bot.settings"
                data.JOIN == "group.join"
                data.LEAVE == "group.leave"
                data.COMMAND == "message.receive.instruction"
                data.BUTTON == "button.report.inline"
                data.MENU == "bot.shortcut.menu"
                
                # 异步执行所有回调
                await asyncio.gather(*[callback(data) for callback in self.callbacks])
                
                return jsonify({'status': 'success'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def add(self, callback: Callable[[DictWithAttr], Awaitable[None]]):
        """添加异步回调函数"""
        if not callable(callback):
            raise ValueError("Callback must be a callable function")
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError("Callback must be an async function")
        self.callbacks.append(callback)
    
    async def start(self, port: int = 5000, path: str = '/webhook'):
        """启动服务器"""
        self.port = port
        self.path = path
        self._setup_routes()
        print(f"Starting webhook server on port {self.port}, path: {self.path}")
        await self.app.run_task(port=self.port, host="0.0.0.0")
    
    def start_in_thread(self, port: int = 5000, path: str = '/webhook'):
        """在新线程中启动服务器"""
        self.port = port
        self.path = path
        self._setup_routes()
        
        def run_server():
            asyncio.run(self.app.run_task(port=port, host="0.0.0.0"))
            
        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()
        return thread
