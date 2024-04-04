import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"debug": False, "silent": False}


@validate(DEFAULTS)
@set_logger()
@authenticate()
def whoami(**kwargs):
    """Return current entity"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["sts"], region=kwargs["region"]
    )

    response = session_objects["sts_client"].get_caller_identity()

    data = {"Arn": response["Arn"], "Region": kwargs["region"]}

    return data
