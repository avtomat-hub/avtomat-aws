import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "enable": False,
    "disable": False,
    "change_kms_key": False,
    "kms_key_id": None,
    "reset_kms_key": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"and": ["change_kms_key", "kms_key_id"]},
    {"at_most_one": ["enable", "disable"]},
    {"at_most_one": ["change_kms_key", "reset_kms_key"]},
    {"at_least_one": ["enable", "disable", "change_kms_key", "reset_kms_key"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def modify_default_ebs_encryption(**kwargs):
    """Modify the default EBS encryption setting"""

    region = kwargs["region"]

    session_objects = set_session_objects(
        kwargs.get("session"), clients=["ec2"], region=region
    )

    logger.info(f"Modifying default EBS encryption setting")

    if kwargs.get("enable"):
        session_objects["ec2_client"].enable_ebs_encryption_by_default()
        logger.info(f"{region}: Enabled default EBS encryption")
    if kwargs.get("disable"):
        session_objects["ec2_client"].disable_ebs_encryption_by_default()
        logger.info(f"{region}: Disabled default EBS encryption")
    if kwargs.get("change_kms_key"):
        session_objects["ec2_client"].modify_ebs_default_kms_key_id(
            KmsKeyId=kwargs["kms_key_id"]
        )
        logger.info(f"{region}: Changed default KMS key to {kwargs['kms_key_id']}")
    if kwargs.get("reset_kms_key"):
        session_objects["ec2_client"].reset_ebs_default_kms_key_id()
        logger.info(f"{region}: Reset default KMS key")

    return
