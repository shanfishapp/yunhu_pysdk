from colorama import init, Fore, Back, Style
from datetime import datetime
# 初始化Colorama（在Windows上自动启用颜色支持）
init(autoreset=True)
class Logger:
    def _write(cls, time, title, msg):
        with open('bot.log', 'a', encoding='utf-8') as file:
            file.write(f"[{title}][{time}]{msg}\n")
    def _get_time(cls):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    def info(cls, msg):
        time = cls._get_time()
        cls._write(time, "INFO", msg)
        print(Fore.GREEN + "[INFO]" + Fore.RESET + Fore.CYAN + f"[{time}]" + Fore.RESET + msg)
    def debug(cls, msg):
        time = cls._get_time()
        cls._write(time, "DEBUG", msg)
        print(Fore.WHITE + "[DEBUG]" + Fore.RESET + Fore.CYAN + f"[{time}]" + Fore.RESET + msg)
    def warning(cls, msg):
        time = cls._get_time()
        cls._write(time, "WARN", msg)
        print(Fore.YELLOW + "[WARN]" + Fore.RESET + Fore.CYAN + f"[{time}]" + Fore.RESET + msg)
    def error(cls, msg):
        time = cls._get_time()
        cls._write(time, "ERROR", msg)
        print(Fore.RED + "[ERROR]" + Fore.RESET + Fore.CYAN + f"[{time}]" + Fore.RESET + msg)