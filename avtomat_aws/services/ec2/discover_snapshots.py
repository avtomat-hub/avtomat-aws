import logging
from datetime import datetime, timezone

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "volume_ids": [],
    "snapshot_ids": [],
    "unencrypted": False,
    "exclude_aws_backup": False,
    "created_before": None,
    "created_after": None,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"date_yymmdd": ["created_before", "created_after"]},
    {"at_most_one": ["snapshot_ids", "volume_ids"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_snapshots(**kwargs):
    """Discover snapshots based on provided criteria"""

    if kwargs.get("created_before"):
        kwargs["created_before"] = datetime.strptime(
            kwargs["created_before"], "%Y/%m/%d"
        )
    if kwargs.get("created_after"):
        kwargs["created_after"] = datetime.strptime(kwargs["created_after"], "%Y/%m/%d")

    logger.info("Discovering snapshots")

    filters = build_filters(**kwargs)
    snapshots = search_snapshots(filters, **kwargs)

    logger.info(f"{len(snapshots)} snapshots found")
    logger.debug(snapshots)

    return snapshots


def build_filters(**kwargs):
    """Construct filters"""

    unencrypted = kwargs.get("unencrypted")
    volume_ids = kwargs.get("volume_ids")
    snapshot_ids = kwargs.get("snapshot_ids")
    exclude_aws_backup = kwargs.get("exclude_aws_backup")

    filters = []
    if unencrypted:
        logger.debug("Filtering for unencrypted snapshots")
        filters.append({"Name": "encrypted", "Values": ["false"]})
    if volume_ids:
        logger.debug(f"Filtering for source volumes: {volume_ids}")
        filters.append({"Name": "volume-id", "Values": volume_ids})
    if exclude_aws_backup:
        logger.debug("Filtering out AWS Backup snapshots")
    if snapshot_ids:
        logger.debug(f"Filtering for snapshots: {snapshot_ids}")

    return filters


def search_snapshots(filters, **kwargs):
    """Search for snapshots in specified region"""

    session = kwargs["session"]
    region = kwargs["region"]
    snapshot_ids = kwargs.get("snapshot_ids")
    created_before = kwargs.get("created_before")
    created_after = kwargs.get("created_after")
    exclude_aws_backup = kwargs.get("exclude_aws_backup")

    session_objects = set_session_objects(session, resources=["ec2"], region=region)
    snapshots = []

    response = session_objects["ec2_resource"].snapshots.filter(
        Filters=filters, OwnerIds=["self"], SnapshotIds=snapshot_ids
    )

    for snapshot in response:
        if created_before and snapshot.start_time > created_before.replace(
            tzinfo=timezone.utc
        ):
            continue
        if created_after and snapshot.start_time < created_after.replace(
            tzinfo=timezone.utc
        ):
            continue
        if exclude_aws_backup and any(
            tag["Key"].startswith("aws:backup") for tag in (snapshot.tags or [])
        ):
            continue
        snapshots.append(snapshot.id)

    return snapshots
