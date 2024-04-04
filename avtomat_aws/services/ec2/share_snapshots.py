import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [
    {"required": ["snapshot_ids", "target_account"]},
    {
        "choice": [
            {"type": ["gp2", "gp3", "io1", "io2", "st1", "sc1", "standard"]},
        ]
    },
    {"at_least_one": ["size", "type", "iops"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def share_snapshots(**kwargs):
    """Share EC2 snapshots with other accounts"""

    # Required parameters
    snapshot_ids = kwargs.pop("snapshot_ids")
    target_account = kwargs.pop("target_account")

    if not snapshot_ids:
        logger.info("No snapshots to share")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Sharing snapshots with account {target_account}")

    snapshots = []
    for snapshot_id in snapshot_ids:
        try:
            session_objects["ec2_client"].modify_snapshot_attribute(
                Attribute="createVolumePermission",
                CreateVolumePermission={"Add": [{"UserId": target_account}]},
                SnapshotId=snapshot_id,
                OperationType="add",
            )
            snapshots.append(snapshot_id)
            logger.info(f"{snapshot_id} - shared")
        except Exception as e:
            logger.error(f"{snapshot_id} - failed to share snapshot - {e}")
            continue

    logger.info(f"{len(snapshots)} snapshots shared")
    logger.debug(snapshots)

    return snapshots
