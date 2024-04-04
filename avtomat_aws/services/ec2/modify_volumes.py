import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "size": None,
    "type": None,
    "iops": None,
    "snapshot": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["volume_ids"]},
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
def modify_volumes(**kwargs):
    """Modify EBS volumes"""

    # Required parameters
    volume_ids = kwargs.pop("volume_ids")

    if not volume_ids:
        logger.info("No volumes to modify")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Modifying volumes")

    snapshots_to_wait = []
    if kwargs.get("snapshot"):
        for volume_id in volume_ids:
            volume = session_objects["ec2_resource"].Volume(volume_id)
            try:
                snapshot = volume.create_snapshot(
                    Description=f"Backup before modification of {volume_id}",
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

    modified_volumes = []
    for volume_id in volume_ids:
        try:
            modify_args = {"VolumeId": volume_id}
            if kwargs.get("size"):
                modify_args["Size"] = kwargs["size"]
            if kwargs.get("type"):
                modify_args["VolumeType"] = kwargs["type"]
            if kwargs.get("iops"):
                modify_args["Iops"] = kwargs["iops"]
            session_objects["ec2_client"].modify_volume(**modify_args)
            modified_volumes.append(volume_id)
            logger.info(f"{volume_id} - modified")
        except Exception as e:
            logger.error(f"{volume_id} - failed to modify - {e}")

    if kwargs.get("size"):
        logger.info(
            "Ensure the server file system is extended to use the newly increased volume size."
        )

    logger.info(f"{len(modified_volumes)} volumes modified")
    logger.debug(modified_volumes)

    return modified_volumes
