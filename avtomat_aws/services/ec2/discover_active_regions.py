import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}


@validate(DEFAULTS)
@set_logger()
@authenticate()
def discover_active_regions(**kwargs):
    """Discover active regions for an account"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=kwargs["region"]
    )

    logger.info("Discovering active regions")

    regions = [
        region["RegionName"]
        for region in session_objects["ec2_client"].describe_regions()["Regions"]
    ]

    logger.info(f"{len(regions)} active regions found.")
    logger.debug(regions)

    return regions
