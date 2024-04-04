import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}


@validate(DEFAULTS)
@set_logger()
@authenticate()
def discover_default_ebs_encryption(**kwargs):
    """Discover the default EBS encryption setting"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=kwargs["region"]
    )

    logger.info("Discovering default EBS encryption")

    enabled = session_objects["ec2_client"].get_ebs_encryption_by_default()[
        "EbsEncryptionByDefault"
    ]
    if enabled:
        kms_key_id = session_objects["ec2_client"].get_ebs_default_kms_key_id()[
            "KmsKeyId"
        ]
        logger.info(f"{kwargs['region']}: Default EBS encryption is enabled")
        logger.info(f"{kwargs['region']}: Default KMS key: {kms_key_id}")

        return {"Region": kwargs["region"], "Enabled": enabled, "KmsKeyId": kms_key_id}

    else:
        logger.info(f"{kwargs['region']}: Default EBS encryption is disabled")

        return {"Region": kwargs["region"], "Enabled": enabled, "KmsKeyId": None}
