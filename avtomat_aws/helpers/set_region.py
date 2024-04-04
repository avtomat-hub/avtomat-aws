import logging
import os

logger = logging.getLogger(__name__)


def set_region(region=None, session=None, debug=None, silent=None):
    """Set the region."""

    # Set logging level
    if debug:
        logger.setLevel(logging.DEBUG)
    elif silent:
        logger.setLevel(logging.WARNING)

    if region:
        logger.debug(f"Region explicitly set")
    elif "AWS_DEFAULT_REGION" in os.environ:
        region = os.environ["AWS_DEFAULT_REGION"]
        logger.debug(f"Region found in environment variables")
    elif session.region_name:
        region = session.region_name
        logger.debug(f"Region found in configuration")
    else:
        region = "us-east-1"
        logger.debug(f"No session default, fallback to 'us-east-1'")

    logger.debug(f"Region - {region}")

    return region
