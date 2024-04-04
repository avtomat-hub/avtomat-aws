import logging

from botocore.exceptions import ClientError

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["user"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def quarantine_user(**kwargs):
    """Disable console and programmatic access and apply AWSCompromisedKeyQuarantineV2 policy to an IAM user"""

    # Required parameters
    user = kwargs.pop("user")

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Quarantining user {user}")

    try:
        session_objects["iam_client"].delete_login_profile(UserName=user)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            pass
        else:
            raise e
    logger.info(f"Console access disabled")

    keys_response = session_objects["iam_client"].list_access_keys(UserName=user)
    for key in keys_response["AccessKeyMetadata"]:
        if key["Status"] == "Active":
            session_objects["iam_client"].update_access_key(
                AccessKeyId=key["AccessKeyId"], Status="Inactive", UserName=user
            )
    logger.info(f"Programmatic access disabled")

    session_objects["iam_client"].attach_user_policy(
        UserName=user, PolicyArn="arn:aws:iam::aws:policy/AWSCompromisedKeyQuarantineV2"
    )
    logger.info(f"AWSCompromisedKeyQuarantineV2 policy attached")
