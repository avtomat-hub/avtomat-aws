import logging

from avtomat_aws.loggers.set_logging import set_logging


def set_logger():
    """Decorator to set a logger for the action."""

    def decorator(func):
        def wrapper(**kwargs):
            # Setup logger
            set_logging()
            logger = logging.getLogger("avtomat_aws")
            # Set log level
            if kwargs.get("debug"):
                logger.setLevel(logging.DEBUG)
            if kwargs.get("silent"):
                logger.setLevel(logging.WARNING)
            # Call the action
            return func(**kwargs)

        return wrapper

    return decorator
