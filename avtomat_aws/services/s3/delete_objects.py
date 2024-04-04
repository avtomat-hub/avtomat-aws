import logging

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
def delete_objects(**kwargs):
    """Delete objects from an S3 bucket"""

    # Required parameters
    bucket = kwargs.pop("bucket")
    objects = kwargs.pop("objects")

    if not objects:
        logger.info("No objects to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["s3"], region=kwargs["region"]
    )

    logger.info(f"Deleting objects from '{bucket}'")

    if len(objects) > 500:
        chunks = [objects[x : x + 500] for x in range(0, len(objects), 500)]
    else:
        chunks = [objects]

    failed = []
    counter = 0
    for chunk in chunks:
        if kwargs.get("prefix"):
            prefix = kwargs["prefix"].rstrip("/")
            delete = {"Objects": [{"Key": f"{prefix}/{obj}"} for obj in chunk]}
        else:
            delete = {"Objects": [{"Key": obj} for obj in chunk]}
        try:
            response = session_objects["s3_client"].delete_objects(
                Bucket=bucket, Delete=delete
            )
            counter += len(response["Deleted"])
            if response.get("Errors"):
                for obj in response["Errors"]:
                    logger.error(
                        f"Failed to delete object: {obj['Key']} - {obj['Code']} - {obj['Message']}"
                    )
                    failed.extend(obj["Key"])
        except Exception as e:
            logger.error(f"Failed to delete objects: {e}")
            failed.extend(chunk)
            continue

    logger.info(f"{counter} objects deleted")
    if failed:
        logger.warning(f"{len(failed)} objects failed to delete")
        logger.debug(failed)

    return failed
