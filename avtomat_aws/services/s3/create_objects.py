import logging
import os

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"prefix": "", "region": None, "debug": False, "silent": False}
RULES = [{"required": ["bucket", "objects"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def create_objects(**kwargs):
    """Create objects in an S3 bucket"""

    # Required parameters
    bucket = kwargs.pop("bucket")
    objects = kwargs.pop("objects")

    if not objects:
        logger.info("No objects to create")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["s3"], region=kwargs["region"]
    )

    logger.info(f"Creating objects in '{bucket}'")

    failed = []
    counter = 0
    for obj in objects:
        key = obj["Key"]
        body = obj["Body"]
        if kwargs.get("prefix"):
            prefix = kwargs["prefix"].rstrip("/")
            key = f"{prefix}/{key}"

        if os.path.isfile(obj["Body"]):
            try:
                with open(body, "rb") as f:
                    body = f.read()
            except Exception as e:
                failed.append(key)
                logger.error(f"{key} - failed to read {body} - {e}")
                continue
        try:
            session_objects["s3_client"].put_object(Bucket=bucket, Key=key, Body=body)
            counter += 1
            logger.debug(f"{key} - created")
        except Exception as e:
            failed.append(key)
            logger.error(f"{key} - failed to create - {e}")

    logger.info(f"{counter} objects created")
    if failed:
        logger.warning(f"{len(failed)} objects failed to create")
        logger.warning(failed)

    return failed
