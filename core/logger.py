"""分级日志系统。"""
import logging
from pathlib import Path
from datetime import datetime


class GameLogger:
    _instance = None

    @classmethod
    def get(cls, name: str = "game") -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._setup(name)
        return cls._instance

    @staticmethod
    def _setup(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logger.addHandler(console)

        # 文件 handler 可能失败（Android 上 cwd 不可写），安全跳过
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_handler = logging.FileHandler(
                log_dir / f"{name}_{timestamp}.log", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"[Logger] 文件日志不可用（安全跳过）: {e}")
        return logger
