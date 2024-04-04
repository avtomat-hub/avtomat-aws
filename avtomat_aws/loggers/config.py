config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"}
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "WARNING"},
        "avtomat_aws": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
}
