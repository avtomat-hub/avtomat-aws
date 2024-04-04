from logging.config import dictConfig

from .config import config


def set_logging():
    """Configure logging"""
    dictConfig(config)
