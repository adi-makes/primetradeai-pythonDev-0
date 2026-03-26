"""Logging configuration for the trading bot."""

import logging
import sys

_configured = False

_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

__all__ = ["get_logger"]


def _configure() -> None:
    """Set up root logger with file and stream handlers (called once)."""
    global _configured
    if _configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # FileHandler → trading_bot.log, append mode, level DEBUG
    file_handler = logging.FileHandler("trading_bot.log", mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FORMAT))

    # StreamHandler → stdout, level INFO
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_FORMAT))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger with handlers attached."""
    _configure()
    return logging.getLogger(name)
