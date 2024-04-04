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
def discover_unused_access_keys(**kwargs):
    """Discover access keys not used over a certain amount of days"""

    # Required parameters
    threshold_days = kwargs.pop("threshold_days")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering access keys not used for more than {threshold_days} days")

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
                    try:
                        last_used = session_objects[
                            "iam_client"
                        ].get_access_key_last_used(AccessKeyId=key["AccessKeyId"])
                    except Exception as e:
                        logger.error(
                            f"Failed to get last used date for {key['AccessKeyId']} - {e}"
                        )
                        continue
                    if "AccessKeyLastUsed" in last_used:
                        age = (
                            datetime.now(timezone.utc)
                            - last_used["AccessKeyLastUsed"]["LastUsedDate"]
                        ).days
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
