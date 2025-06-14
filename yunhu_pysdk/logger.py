import logging
import sys
from colorama import init, Fore, Back, Style

# 初始化颜色支持
init(autoreset=True)

class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt='%Y-%m-%d %H:%M:%S'):
        super().__init__(fmt or '%(asctime)s %(levelname)s: %(message)s', datefmt=datefmt)

    def format(self, record):
        time_part = f"{Fore.CYAN}[{self.formatTime(record)}]"
        level_color = {
            logging.DEBUG: "",
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: f"{Back.RED}{Fore.BLACK}"
        }.get(record.levelno, "")
        level_part = f"{level_color}[{record.levelname}]"
        return f"{time_part}{level_part} {record.getMessage()}"

def setup_logger(name='BotLogger', log_file='bot.log', level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()