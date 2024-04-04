import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"include_snapshots": False, "region": None, "debug": False, "silent": False}
RULES = [{"required": ["image_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_images(**kwargs):
    """Delete EC2 images (AMI)"""

    # Required parameters
    image_ids = kwargs.pop("image_ids")

    if not image_ids:
        logger.info("No images to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    if kwargs.get("include_snapshots"):
        logger.info(f"Deleting images and associated snapshots")
    else:
        logger.info(f"Deleting images")

    snapshot_ids = []
    failed = []
    counter = 0
    for image_id in image_ids:
        try:
            image = session_objects["ec2_resource"].Image(image_id)
            if kwargs.get("include_snapshots"):
                for block_device in image.block_device_mappings:
                    if "Ebs" in block_device:
                        snapshot_ids.append(block_device["Ebs"]["SnapshotId"])
            image.deregister()
            counter += 1
            logger.info(f"{image_id} - deleted")
        except Exception as e:
            failed.append(image_id)
            logger.error(f"{image_id} - failed to delete - {e}")

    if snapshot_ids:
        delete_snapshots(snapshot_ids, session_objects)

    logger.info(f"{counter} images deleted")
    if failed:
        logger.warning(f"{len(failed)} images failed to delete")
        logger.debug(failed)

    return failed


def delete_snapshots(snapshot_ids, session_objects):
    """Delete EBS snapshots"""

    for snapshot_id in snapshot_ids:
        try:
            snapshot = session_objects["ec2_resource"].Snapshot(snapshot_id)
            snapshot.delete()
            logger.debug(f"{snapshot_id} - deleted")
        except Exception as e:
            logger.error(f"{snapshot_id} - failed to delete - {e}")
