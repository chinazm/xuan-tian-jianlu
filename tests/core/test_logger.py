import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import GameLogger
import logging


def test_logger_creates_instance():
    logger = GameLogger.get("test_logger")
    assert isinstance(logger, logging.Logger)


def test_logger_has_handlers():
    logger = GameLogger.get("test_handlers")
    assert len(logger.handlers) >= 2  # console + file


def test_singleton_pattern():
    logger1 = GameLogger.get("test_singleton")
    logger2 = GameLogger.get("test_singleton")
    assert logger1 is logger2


if __name__ == "__main__":
    test_logger_creates_instance()
    test_logger_has_handlers()
    test_singleton_pattern()
    print("All logger tests passed!")
