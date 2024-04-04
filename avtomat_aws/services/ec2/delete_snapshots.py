import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["snapshot_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_snapshots(**kwargs):
    """Delete EBS snapshots"""

    # Required parameters
    snapshot_ids = kwargs.pop("snapshot_ids")

    if not snapshot_ids:
        logger.info("No snapshots to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Deleting snapshots")

    failed = []
    counter = 0
    for snapshot_id in snapshot_ids:
        try:
            snapshot = session_objects["ec2_resource"].Snapshot(snapshot_id)
            snapshot.delete()
            counter += 1
            logger.info(f"{snapshot_id} - deleted")
        except Exception as e:
            failed.append(snapshot_id)
            logger.error(f"{snapshot_id} - failed to delete - {e}")

    logger.info(f"{counter} snapshots deleted")
    if failed:
        logger.warning(f"{len(failed)} snapshots failed to delete")
        logger.debug(failed)

    return failed
