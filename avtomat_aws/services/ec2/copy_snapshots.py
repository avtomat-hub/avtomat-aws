import logging
import time

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "region": None,
    "pending_limit": 20,
    "encrypt": False,
    "kms_key_id": None,
    "debug": False,
    "silent": False,
}
RULES = [{"and": ["encrypt", "kms_key_id"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def copy_snapshots(**kwargs):
    """Move EC2 snapshots between regions or accounts"""

    # Required parameters
    target_region = kwargs.pop("target_region")
    snapshot_ids = kwargs.pop("snapshot_ids")

    if not snapshot_ids:
        logger.info("No snapshots to copy")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=target_region
    )

    logger.info(f"Creating snapshot copies in {target_region}")

    snapshots = []
    pending_snapshots = set()
    pending_limit = kwargs["pending_limit"]
    logger.debug(f"Custom pending limit: {pending_limit}")

    for snapshot_id in snapshot_ids:
        while len(pending_snapshots) >= pending_limit:
            logger.debug(f"Reached {pending_limit} pending snapshots, waiting...")
            for snapshot in list(pending_snapshots):
                status = session_objects["ec2_client"].describe_snapshots(
                    SnapshotIds=[snapshot]
                )["Snapshots"][0]["State"]
                if status != "pending":
                    pending_snapshots.remove(snapshot)
            time.sleep(30)

        try:
            copy_args = {
                "SourceRegion": kwargs["region"],
                "SourceSnapshotId": snapshot_id,
                "Description": f"Copy of {snapshot_id} in {kwargs['region']}",
            }

            if kwargs.get("kms_key_id"):
                copy_args["KmsKeyId"] = kwargs["kms_key_id"]
            if kwargs.get("encrypt"):
                copy_args["Encrypted"] = True

            response = session_objects["ec2_client"].copy_snapshot(**copy_args)
            logger.info(f"{snapshot_id} - copying as {response['SnapshotId']}")
            pending_snapshots.add(response["SnapshotId"])
            snapshots.append(response["SnapshotId"])
        except Exception as e:
            logger.error(f"{snapshot_id} - failed to copy snapshot - {e}")
            continue

    logger.info(f"{len(snapshots)} snapshots copied")
    logger.debug(snapshots)

    return snapshots
