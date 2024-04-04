import logging
from datetime import datetime, timezone

from botocore.exceptions import ClientError

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["threshold_days"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_old_password_users(threshold_days, **kwargs):
    """Discover IAM users with passwords older than a certain age"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering users with passwords over {threshold_days} days old")

    users = []
    users_response = session_objects["iam_client"].list_users(MaxItems=50)
    while True:
        for user in users_response["Users"]:
            try:
                password_create_date = session_objects["iam_client"].get_login_profile(
                    UserName=user["UserName"]
                )["LoginProfile"]["CreateDate"]
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchEntity":
                    continue
                else:
                    logger.error(
                        f"Failed to get password create date for {user['UserName']} - {e}"
                    )
                    continue
            age = (datetime.now(timezone.utc) - password_create_date).days
            if age > threshold_days:
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
