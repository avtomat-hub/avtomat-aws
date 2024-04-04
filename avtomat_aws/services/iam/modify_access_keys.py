import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "enable": False,
    "disable": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["keys"]},
    {"at_least_one": ["enable", "disable"]},
    {"at_most_one": ["enable", "disable"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def modify_access_keys(**kwargs):
    """Disable specific access keys"""

    # Required parameters
    keys = kwargs.pop("keys")

    if not keys:
        logger.info("No access keys to modify")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    if kwargs.get("disable"):
        logger.info(f"Disabling access keys")
        status = "Inactive"
    elif kwargs.get("enable"):
        logger.info(f"Enabling access keys")
        status = "Active"
    else:
        raise ValueError("No action specified")
    logger.debug(f"Keys: {keys}")

    failed = []
    counter = 0
    for key in keys:
        access_key_id = key["AccessKeyId"]
        username = key["UserName"]

        try:
            session_objects["iam_client"].update_access_key(
                AccessKeyId=access_key_id, Status=status, UserName=username
            )
            logger.debug(f"{access_key_id} - {status}")
            counter += 1
        except Exception as e:
            failed.append(access_key_id)
            logger.error(f"{access_key_id} - failed to update - {e}")
            continue

    if kwargs.get("disable"):
        logger.info(f"Disabled {counter} access keys")
    elif kwargs.get("enable"):
        logger.info(f"Enabled {counter} access keys")
    if failed:
        logger.warning(f"{len(failed)} access keys failed to update")
        logger.debug(failed)

    return failed
