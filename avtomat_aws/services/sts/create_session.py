import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate

logger = logging.getLogger(__name__)

action_description = "Create an authenticated session."

DEFAULTS = {
    "access_key": None,
    "secret_key": None,
    "session_token": None,
    "profile": None,
    "role_arn": None,
    "mfa_serial": None,
    "mfa_token": None,
    "debug": False,
    "silent": False,
}
RULES = [{"and": ["mfa_token", "mfa_serial"]}, {"and": ["access_key", "secret_key"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def create_session(**kwargs):
    """Create an authenticated session"""
    return kwargs["session"]
