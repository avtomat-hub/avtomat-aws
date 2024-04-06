import logging

import boto3

logger = logging.getLogger(__name__)


def set_session(**kwargs):
    """Set the session."""

    # Set logging level
    if kwargs.get("debug"):
        logger.setLevel(logging.DEBUG)
    if kwargs.get("silent"):
        logger.setLevel(logging.WARNING)

    if kwargs.get("session"):
        logger.debug("Session explicitly supplied.")
        session = kwargs["session"]
    elif kwargs.get("profile"):
        session = authenticate_profile(kwargs["profile"])
    elif kwargs.get("role_arn"):
        session = authenticate_role(
            kwargs["role_arn"], kwargs["mfa_serial"], kwargs["mfa_token"]
        )
    elif kwargs.get("access_key") and kwargs.get("secret_key"):
        session = authenticate_credentials(
            kwargs["access_key"], kwargs["secret_key"], kwargs["session_token"]
        )
    else:
        logger.debug(
            "No 'session' or 'profile' or 'role_arn' or 'access_key' + 'secret_key' parameters supplied. "
            "Falling back to default credentials."
        )
        session = authenticate_default()

    sts_client = session.client("sts")
    response = sts_client.get_caller_identity()
    logger.debug(f"Session created: {response['Arn']}")

    return session


def authenticate_credentials(access_key, secret_key, session_token=None):
    """Authenticate with credentials"""

    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
    )


def authenticate_profile(profile_name):
    """Authenticate with a profile"""

    return boto3.Session(profile_name=profile_name)


def authenticate_role(role_arn, mfa_serial=None, mfa_token=None):
    """Authenticate by assuming a role"""

    sts_client = boto3.client("sts")
    response = sts_client.get_caller_identity()
    if ":" in response["UserId"]:
        parts = response["UserId"].split(":")
        user = parts[1]
    else:
        user = response["UserId"]

    assume_role_kwargs = {
        "RoleArn": role_arn,
        "RoleSessionName": user,
    }

    if mfa_serial:
        assume_role_kwargs["SerialNumber"] = mfa_serial
        assume_role_kwargs["TokenCode"] = mfa_token

    response = sts_client.assume_role(**assume_role_kwargs)
    credentials = response["Credentials"]

    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )


def authenticate_default():
    """Authenticate with default credentials"""

    return boto3.Session()
