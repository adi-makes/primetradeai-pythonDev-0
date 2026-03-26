"""Logging configuration for the trading bot."""

import logging
import sys
from pathlib import Path

_configured = False

_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

__all__ = ["get_logger"]


def _configure() -> None:
    """Set up root logger with file and stream handlers (called once)."""
    global _configured
    if _configured:
        return

    root_logger = logging.getLogger()
    # Keep the console clean and only emit debug from our own package when needed.
    root_logger.setLevel(logging.INFO)

    # Reduce noise from third-party libraries.
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # FileHandler → trading_bot/trading_bot.log, append mode, level DEBUG
    log_path = Path(__file__).resolve().parent.parent / "trading_bot.log"
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT))

    # StreamHandler → stdout, level INFO
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_FORMAT))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # Allow debug-level logs from our own code into the file.
    logging.getLogger("trading_bot").setLevel(logging.DEBUG)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with handlers attached."""
    _configure()
    return logging.getLogger(name)
