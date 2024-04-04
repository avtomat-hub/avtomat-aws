import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["security_group_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_security_groups(**kwargs):
    """Delete EC2 security groups"""

    # Required parameters
    security_group_ids = kwargs.pop("security_group_ids")

    if not security_group_ids:
        logger.info("No security groups to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Deleting security groups")

    failed = []
    counter = 0
    for security_group_id in security_group_ids:
        try:
            session_objects["ec2_client"].delete_security_group(
                GroupId=security_group_id
            )
            counter += 1
            logger.info(f"{security_group_id} - deleted")
        except Exception as e:
            failed.append(security_group_id)
            logger.error(f"{security_group_id} - failed to delete - {e}")

    logger.info(f"{counter} security groups deleted")
    if failed:
        logger.warning(f"{len(failed)} security groups failed to delete")
        logger.debug(failed)

    return failed
