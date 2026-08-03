"""Centralized logging for the application."""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_FILE = os.path.join(LOG_DIR, "errors.log")

MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


_fmt = logging.Formatter(
    "%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def _make_file_handler(path: str, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(path, encoding="utf-8",
                                  maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    handler.setLevel(level)
    handler.setFormatter(_fmt)
    return handler


# Handlers مشتركة على مستوى الوحدة: كل loggers يشاركون نفس المقبض على الملف
# حتى لا يفشل التدوير عند 5MB (كان كل logger ينشئ handler خاصاً على نفس الملف
# فيتعذر إعادة تسمية app.log لأن مقبضاً آخر ما زال مفتوحاً — Windows PermissionError)
_FILE_HANDLER = _make_file_handler(LOG_FILE, logging.DEBUG)
_ERROR_HANDLER = _make_file_handler(ERROR_FILE, logging.WARNING)
_CONSOLE_HANDLER = logging.StreamHandler()
_CONSOLE_HANDLER.setLevel(logging.WARNING)
_CONSOLE_HANDLER.setFormatter(_fmt)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_FILE_HANDLER)
        logger.addHandler(_ERROR_HANDLER)
        logger.addHandler(_CONSOLE_HANDLER)
    return logger


def read_log(max_lines=200, level_filter=None):
    """Read the last N lines from app.log optionally filtered by level."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if level_filter:
        lines = [l for l in lines if f"| {level_filter.upper()}" in l]
    return lines[-max_lines:]


def read_errors(max_lines=100):
    """Read recent error entries."""
    if not os.path.exists(ERROR_FILE):
        return []
    with open(ERROR_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines[-max_lines:]


def get_log_stats():
    """Get statistics about logs."""
    if not os.path.exists(LOG_FILE):
        return {"total": 0, "info": 0, "warning": 0, "error": 0, "debug": 0}
    stats = {"total": 0, "info": 0, "warning": 0, "error": 0, "debug": 0}
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            stats["total"] += 1
            if "| INFO" in line:
                stats["info"] += 1
            elif "| WARNING" in line:
                stats["warning"] += 1
            elif "| ERROR" in line:
                stats["error"] += 1
            elif "| DEBUG" in line:
                stats["debug"] += 1
    return stats
