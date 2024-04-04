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
def discover_inactive_console_users(**kwargs):
    """Discover IAM users with last console sign-in over a certain period"""

    # Required parameters
    threshold_days = kwargs.pop("threshold_days")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(
        f"Discovering users with last console sign-in over {threshold_days} days"
    )

    users = []
    users_response = session_objects["iam_client"].list_users(MaxItems=50)
    while True:
        for user in users_response["Users"]:
            try:
                password_last_used = (
                    session_objects["iam_client"]
                    .get_user(UserName=user["UserName"])["User"]
                    .get("PasswordLastUsed")
                )
            except Exception as e:
                logger.error(
                    f"Failed to get last console sign-in for {user['UserName']} - {e}"
                )
                continue
            try:
                console_access = session_objects["iam_client"].get_login_profile(
                    UserName=user["UserName"]
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchEntity":
                    continue
                else:
                    logger.error(
                        f"Failed to get console access status for {user['UserName']} - {e}"
                    )
                    continue

            if password_last_used:
                age = (datetime.now(timezone.utc) - password_last_used).days
                if age > threshold_days:
                    users.append({"UserName": user["UserName"]})
            elif console_access.get("LoginProfile"):
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
