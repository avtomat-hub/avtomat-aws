import logging
from datetime import datetime, timezone

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
def discover_inactive_users(**kwargs):
    """Discover IAM users who haven't used the console and any access keys over a certain period"""

    # Required parameters
    threshold_days = kwargs.pop("threshold_days")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering users with last activity over {threshold_days} days")

    users = []
    users_response = session_objects["iam_client"].list_users(MaxItems=50)
    while True:
        for user in users_response["Users"]:
            try:
                access_keys_recently_used = check_access_keys_recently_used(
                    user, threshold_days, session_objects
                )
                password_recently_used = check_password_recently_used(
                    user, threshold_days, session_objects
                )
            except Exception as e:
                logger.error(
                    f"Failed to check user activity for {user['UserName']} - {e}"
                )
                continue

            if not access_keys_recently_used and not password_recently_used:
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


def check_access_keys_recently_used(user, threshold_days, session_objects):
    """Check if user has used any access keys within the threshold days"""

    keys_response = session_objects["iam_client"].list_access_keys(
        UserName=user["UserName"]
    )

    for key in keys_response["AccessKeyMetadata"]:
        last_used = session_objects["iam_client"].get_access_key_last_used(
            AccessKeyId=key["AccessKeyId"]
        )

        if "LastUsedDate" in last_used["AccessKeyLastUsed"]:
            age = (
                datetime.now(timezone.utc)
                - last_used["AccessKeyLastUsed"]["LastUsedDate"]
            ).days
            if age < threshold_days:
                return True

    return False


def check_password_recently_used(user, threshold_days, session_objects):
    """Check if user has used their password within the threshold days"""

    password_last_used = (
        session_objects["iam_client"]
        .get_user(UserName=user["UserName"])["User"]
        .get("PasswordLastUsed")
    )

    if password_last_used:
        age = (datetime.now(timezone.utc) - password_last_used).days
        if age < threshold_days:
            return True

    return False
