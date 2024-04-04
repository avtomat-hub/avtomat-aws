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
def discover_unused_roles(**kwargs):
    """Discover IAM roles not used over a certain amount of days"""

    # Required parameters
    threshold_days = kwargs.pop("threshold_days")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering roles not used for more than {threshold_days} days")

    roles = []
    roles_response = session_objects["iam_client"].list_roles(MaxItems=100)
    while True:
        for role in roles_response["Roles"]:
            try:
                last_used = (
                    session_objects["iam_client"]
                    .get_role(RoleName=role["RoleName"])["Role"]
                    .get("RoleLastUsed")
                )
            except Exception as e:
                logger.error(
                    f"Failed to get last used date for {role['RoleName']} - {e}"
                )
                continue
            if last_used:
                age = (datetime.now(timezone.utc) - last_used["LastUsedDate"]).days
                if age > threshold_days:
                    roles.append(role["RoleName"])
        if roles_response["IsTruncated"]:
            roles_response = session_objects["iam_client"].list_roles(
                Marker=roles_response["Marker"]
            )
        else:
            break

    logger.info(f"{len(roles)} roles found")
    logger.debug(roles)

    return roles
