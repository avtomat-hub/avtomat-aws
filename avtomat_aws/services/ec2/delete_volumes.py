import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"snapshot": False, "region": None, "debug": False, "silent": False}
RULES = [{"required": ["volume_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_volumes(**kwargs):
    """Delete EBS volumes"""

    # Required parameters
    volume_ids = kwargs.pop("volume_ids")

    if not volume_ids:
        logger.info("No volumes to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Deleting volumes")
    if kwargs.get("snapshot"):
        logger.info("Creating snapshots before deletion")

    snapshots_to_wait = []
    for volume_id in volume_ids:
        volume = session_objects["ec2_resource"].Volume(volume_id)
        if volume.state == "in-use":
            logger.warning(f"{volume_id} - in use, skipping")
            continue

        if kwargs.get("snapshot") and volume.state == "available":
            try:
                snapshot = volume.create_snapshot(
                    Description=f"Backup before deletion of {volume_id}",
                    TagSpecifications=[
                        {
                            "ResourceType": "snapshot",
                            "Tags": [{"Key": "Name", "Value": f"source:{volume_id}"}],
                        }
                    ],
                )
                logger.info(f"{volume_id} - creating {snapshot.id}")
                snapshots_to_wait.append(snapshot)
            except Exception as e:
                logger.error(f"{volume_id} - failed to create snapshot - {e}")
                continue

    for snapshot in snapshots_to_wait:
        snapshot.wait_until_completed()

    failed = []
    counter = 0
    for volume_id in volume_ids:
        try:
            volume = session_objects["ec2_resource"].Volume(volume_id)
            if volume.state != "available":
                continue
            volume.delete()
            counter += 1
            logger.info(f"{volume_id} - deleted")
        except Exception as e:
            failed.append(volume_id)
            logger.error(f"{volume_id} - failed to delete - {e}")
            continue

    logger.info(f"{counter} volumes deleted")
    if failed:
        logger.warning(f"{len(failed)} volumes failed to delete")
        logger.debug(failed)

    return failed
