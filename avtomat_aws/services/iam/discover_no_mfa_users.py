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
def discover_no_mfa_users(**kwargs):
    """Discover IAM users without MFA enabled"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering users without MFA enabled")

    users = []
    users_response = session_objects["iam_client"].list_users(MaxItems=50)
    while True:
        for user in users_response["Users"]:
            try:
                mfa_response = session_objects["iam_client"].list_mfa_devices(
                    UserName=user["UserName"]
                )
            except Exception as e:
                logger.error(f"Failed to list MFA devices for {user['UserName']} - {e}")
                continue
            if not mfa_response["MFADevices"]:
                users.append({"UserName": user["UserName"]})
        if users_response["IsTruncated"]:
            users_response = session_objects["iam_client"].list_users(
                Marker=users_response["Marker"]
            )
        else:
            break

    logger.info(f"{len(users)} users found")
    logger.debug(users)

    return users
