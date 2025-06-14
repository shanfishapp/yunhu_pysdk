import logging
import sys
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import asyncio
from typing import Optional
from colorama import init, Fore, Back, Style

# 初始化colorama（自动重置颜色）
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    """自定义带颜色的日志格式化器"""
    def __init__(self):
        super().__init__(datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        # 时间部分 - 青色
        time_part = f"{Fore.CYAN}[{self.formatTime(record, self.datefmt)}]"
        
        # 根据日志级别设置颜色
        if record.levelno == logging.DEBUG:
            level_part = f"{Style.RESET_ALL}[{record.levelname}]"
        elif record.levelno == logging.INFO:
            level_part = f"{Fore.GREEN}[{record.levelname}]"
        elif record.levelno == logging.WARNING:
            level_part = f"{Fore.YELLOW}[{record.levelname}]"
        elif record.levelno == logging.ERROR:
            level_part = f"{Fore.RED}[{record.levelname}]"
        elif record.levelno == logging.CRITICAL:
            level_part = f"{Back.RED}{Fore.BLACK}[{record.levelname}]{Back.RESET}"
        
        # 消息内容为白色
        msg_part = f"{Style.RESET_ALL}{record.getMessage()}"
        return f"{time_part}{level_part} {msg_part}"

class Logger:
    _instance = None  # 单例实例
    _lock = asyncio.Lock()  # 异步锁
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self, name: str = "BotLogger", log_file: str = "bot.log", level: int = logging.INFO):
        if self.__initialized:
            return
        self.__initialized = True
        
        self.log_queue = Queue()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 移除所有现有处理器（避免重复添加）
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 控制台处理器（带颜色）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColorFormatter())
        
        # 文件处理器（无颜色）
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s][%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        
        # 初始化队列监听器
        self.listener = QueueListener(self.log_queue, console_handler, file_handler)
        self.listener.start()
        
        # 添加唯一的队列处理器
        self.logger.addHandler(QueueHandler(self.log_queue))
    
    async def log(self, level: int, message: str, code: Optional[int] = None):
        """异步记录日志"""
        async with self._lock:  # 确保线程安全
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self._sync_log(level, message, code)
            )
    
    def _sync_log(self, level: int, message: str, code: Optional[int]):
        """同步记录日志（内部方法）"""
        self.logger.log(level, message)
        if code is not None and code != 0:
            self.listener.stop()
            sys.exit(code)
    
    async def debug(self, message: str):
        await self.log(logging.DEBUG, message)
    
    async def info(self, message: str):
        await self.log(logging.INFO, message)
    
    async def warning(self, message: str):
        await self.log(logging.WARNING, message)
    
    async def error(self, message: str, code: Optional[int] = None):
        await self.log(logging.ERROR, message, code)
    
    async def critical(self, message: str, code: Optional[int] = None):
        await self.log(logging.CRITICAL, message, code)
    
    def shutdown(self):
        """安全关闭日志监听器"""
        self.listener.stop()

# 全局唯一的 Logger 实例
logger = Logger()