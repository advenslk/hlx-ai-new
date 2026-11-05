"""
HELZERX AI Support - Structured Logging Module
Provides standardized colored console output and rotating file logs.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "helzerx_bot.log"


class ANSIColorFormatter(logging.Formatter):
    """Formats log records with ANSI color codes for readable console output."""
    COLORS = {
        logging.DEBUG: "\033[36m",     # Cyan
        logging.INFO: "\033[32m",      # Green
        logging.WARNING: "\033[33m",   # Yellow
        logging.ERROR: "\033[31m",     # Red
        logging.CRITICAL: "\033[1;31m" # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = f"{record.levelname:<8}"
        msg = record.getMessage()
        name = f"[{record.name}]"
        return f"\033[90m{timestamp}\033[0m {color}{level}{self.RESET} \033[35m{name}\033[0m {msg}"


def setup_logger(name: str = "helzerx") -> logging.Logger:
    """Creates or retrieves a logger configured with console and file handlers."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ANSIColorFormatter())
    logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

    return logger


logger = setup_logger("helzerx")
