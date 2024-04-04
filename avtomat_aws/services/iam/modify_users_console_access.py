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
    {"required": ["users"]},
    {"at_least_one": ["enable", "disable"]},
    {"at_most_one": ["enable", "disable"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def modify_users_console_access(**kwargs):
    """Enable or disable AWS Management Console access for an IAM user"""

    # Needs a validation rule
    if kwargs.get("enable"):
        missing_passwords = [
            user for user in kwargs["users"] if not user.get("Password")
        ]
        if missing_passwords:
            missing_usernames = ", ".join(
                [user["UserName"] for user in missing_passwords]
            )
            raise ValueError(
                f"Password is required when enabling console access for users: {missing_usernames}"
            )

    # Required parameters
    users = kwargs.pop("users")

    if not users:
        logger.info("No users to modify")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    if kwargs.get("enable"):
        logger.info(f"Enabling console access for users")
    elif kwargs.get("disable"):
        logger.info(f"Disabling console access for users")
    logger.debug(f"Users: {users}")

    failed = []
    counter = 0
    if kwargs.get("enable"):
        for user in users:
            username = user["UserName"]
            password = user["Password"]
            try:
                session_objects["iam_client"].create_login_profile(
                    UserName=username, Password=password, PasswordResetRequired=True
                )
                session_objects["iam_client"].attach_user_policy(
                    UserName=username,
                    PolicyArn="arn:aws:iam::aws:policy/IAMUserChangePassword",
                )
                counter += 1
            except Exception as e:
                failed.append(username)
                logger.error(f"{username} - failed to enable console access - {e}")
                continue
    elif kwargs.get("disable"):
        for user in users:
            username = user["UserName"]
            try:
                session_objects["iam_client"].delete_login_profile(UserName=username)
                counter += 1
            except Exception as e:
                failed.append(username)
                logger.error(f"{username} - failed to disable console access - {e}")
                continue

    if kwargs.get("enable"):
        logger.info(f"Enabled console access for {counter} users")
    elif kwargs.get("disable"):
        logger.info(f"Disabled console access for {counter} users")
    if failed:
        logger.warning(f"{len(failed)} users failed to update")
        logger.debug(failed)

    return failed
