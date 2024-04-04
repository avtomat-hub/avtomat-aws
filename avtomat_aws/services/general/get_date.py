import datetime
import logging

from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate

logger = logging.getLogger(__name__)

DEFAULTS = {
    "after": None,
    "before": None,
    "format": "datetime",
    "debug": False,
    "silent": False,
}
RULES = [
    {"at_most_one": ["after", "before"]},
    {"choice": [{"format": ["datetime", "string", "iso"]}]},
]


@validate(DEFAULTS, RULES)
@set_logger()
def get_date(**kwargs):
    """Return a date in the requested format."""

    date_format = kwargs.get("format")
    string_format = "%Y/%m/%d"

    # Determine date
    now = datetime.datetime.utcnow()  # UTC
    if kwargs.get("after"):
        logger.info(f"Returning date {kwargs['after']} days in the future")
        delta = datetime.timedelta(days=kwargs["after"])
        date = now + delta
    elif kwargs.get("before"):
        logger.info(f"Returning date {kwargs['before']} days in the past")
        delta = datetime.timedelta(days=-kwargs["before"])
        date = now + delta
    else:
        logger.info("Returning current date")
        date = now

    # Determine output format
    if date_format == "string":
        date = date.strftime(string_format)
    elif date_format == "iso":
        date = date.isoformat()
    else:
        date = date

    logger.info(f"Date: {date}")

    return date
