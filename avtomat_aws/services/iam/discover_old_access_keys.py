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
def discover_old_access_keys(**kwargs):
    """Discover access keys over a certain age"""

    # Required parameters
    threshold_days = kwargs.pop("threshold_days")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering access keys over {threshold_days} days old")

    access_keys = []
    users_response = session_objects["iam_client"].list_users(MaxItems=50)
    while True:
        for user in users_response["Users"]:
            try:
                keys_response = session_objects["iam_client"].list_access_keys(
                    UserName=user["UserName"]
                )
            except Exception as e:
                logger.error(f"Failed to list access keys for {user['UserName']} - {e}")
                continue
            for key in keys_response["AccessKeyMetadata"]:
                if key["Status"] == "Active":
                    age = (datetime.now(timezone.utc) - key["CreateDate"]).days
                    if age > threshold_days:
                        access_keys.append(
                            {
                                "UserName": user["UserName"],
                                "AccessKeyId": key["AccessKeyId"],
                            }
                        )
        if users_response["IsTruncated"]:
            users_response = session_objects["iam_client"].list_users(
                Marker=users_response["Marker"]
            )
        else:
            break

    logger.info(f"{len(access_keys)} access keys found")
    logger.debug(access_keys)

    return access_keys
