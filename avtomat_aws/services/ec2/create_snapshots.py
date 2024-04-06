import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["volume_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def create_snapshots(**kwargs):
    """Create EBS snapshots from volumes"""

    # Required parameters
    volume_ids = kwargs.pop("volume_ids")

    if not volume_ids:
        logger.info("No volumes to create snapshots from")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Creating snapshots")

    snapshots = []
    failed = []
    for volume_id in volume_ids:
        try:
            volume = session_objects["ec2_resource"].Volume(volume_id)
            snapshot = volume.create_snapshot(
                Description=f"Snapshot of {volume_id}",
                TagSpecifications=[
                    {
                        "ResourceType": "snapshot",
                        "Tags": [{"Key": "Name", "Value": f"source:{volume_id}"}],
                    }
                ],
            )
            logger.info(f"{volume_id} - creating {snapshot.id}")
            snapshots.append(snapshot.id)
        except Exception as e:
            failed.append(volume_id)
            logger.error(f"{volume_id} - failed to create snapshot - {e}")
            continue

    for snapshot in snapshots:
        snapshot = session_objects["ec2_resource"].Snapshot(snapshot)
        snapshot.wait_until_completed()

    logger.info(f"{len(snapshots)} snapshots created")
    if failed:
        logger.warning(f"{len(failed)} volumes failed the snapshot creation process")
        logger.debug(failed)

    return snapshots
