import json
import os
from pathlib import Path
from yunhu_pysdk.logger import Logger

class sdk:
    _config_path = Path("config.json")  # 配置文件路径
    logger = Logger()

    @classmethod
    def init(cls, token, data=True):
        """将 Token 存储到 config.json"""
        try:
            # 写入配置文件
            with open(cls._config_path, "w") as f:
                json.dump({"token": token}, f)
            cls.logger.info(f"Token 已保存到 {cls._config_path}")
        except Exception as e:
            cls.logger.error(f"保存 Token 失败: {e}")
            exit(1)
        if data == True:
            cls.logger.debug("正在加载Webhook数据....")
            

    @classmethod
    def get(cls):
        """从 config.json 读取 Token"""
        try:
            if not cls._config_path.exists():
                cls.logger.error("配置文件不存在，请先调用 init(token)")
                exit(1)
            
            with open(cls._config_path, "r") as f:
                config = json.load(f)
                return config["token"]
        except Exception as e:
            cls.logger.error(f"读取 Token 失败: {e}")
            exit(1)