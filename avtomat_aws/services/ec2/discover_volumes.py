import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "instance_ids": [],
    "volume_ids": [],
    "unencrypted": False,
    "detached": False,
    "types": None,
    "root": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {
        "choice": [
            {"types": ["gp2", "gp3", "io1", "io2", "st1", "sc1", "standard"]},
        ]
    },
    {"at_most_one": ["instance_ids", "volume_ids"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_volumes(**kwargs):
    """Discover EBS volumes based on provided criteria"""

    logger.info("Discovering volumes")

    filters = build_filters(**kwargs)
    volumes = search_volumes(filters, **kwargs)

    logger.info(f"{len(volumes)} volumes found")
    logger.debug(volumes)

    return volumes


def build_filters(**kwargs):
    """Construct filters"""

    instance_ids = kwargs.get("instance_ids")
    volume_ids = kwargs.get("volume_ids")
    unencrypted = kwargs.get("unencrypted")
    detached = kwargs.get("detached")
    types = kwargs.get("types")
    root = kwargs.get("root")

    filters = []
    if instance_ids:
        logger.debug(f"Targeting instance volumes: {instance_ids}")
        filters.append({"Name": "attachment.instance-id", "Values": instance_ids})
    elif volume_ids:
        logger.debug(f"Targeting specific volumes: {volume_ids}")
    else:
        logger.debug("Targeting all volumes")
    if unencrypted:
        logger.debug("Filtering for unencrypted volumes")
        filters.append({"Name": "encrypted", "Values": ["false"]})
    if detached:
        logger.debug("Filtering for detached volumes")
        filters.append({"Name": "status", "Values": ["available"]})
    if types:
        logger.debug(f"Filtering for types: {types}")
        filters.append({"Name": "volume-type", "Values": types})
    if root:
        logger.debug("Filtering for root volumes")
        root_devices = get_root_devices(**kwargs)
        filters.append({"Name": "attachment.device", "Values": root_devices})

    return filters


def search_volumes(filters, **kwargs):
    """Search for volumes in specified region"""

    session = kwargs["session"]
    region = kwargs["region"]
    volume_ids = kwargs.get("volume_ids")

    session_objects = set_session_objects(session, resources=["ec2"], region=region)
    volumes = []

    response = session_objects["ec2_resource"].volumes.filter(
        Filters=filters, VolumeIds=volume_ids
    )

    for volume in response:
        volumes.append(volume.id)

    return volumes


def get_root_devices(**kwargs):
    """Get root devices for specified instances"""

    session = kwargs["session"]
    region = kwargs["region"]
    instance_ids = kwargs.get("instance_ids")

    session_objects = set_session_objects(session, resources=["ec2"], region=region)

    root_devices = []
    for instance in session_objects["ec2_resource"].instances.filter(
        InstanceIds=instance_ids
    ):
        root_devices.append(instance.root_device_name)

    return list(set(root_devices))
