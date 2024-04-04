import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"re_encrypt": False, "region": None, "debug": False, "silent": False}
RULES = [{"required": ["instance_id", "kms_key_id"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def encrypt_instance_volumes(**kwargs):
    """Encrypt all instance volumes with a KMS key"""

    # Required parameters
    instance_id = kwargs.pop("instance_id")
    kms_key_id = kwargs.pop("kms_key_id")

    session_objects = set_session_objects(
        kwargs.get("session"),
        clients=["ec2"],
        resources=["ec2"],
        region=kwargs["region"],
    )

    logger.info(f"{instance_id} - encrypting volumes with {kms_key_id}")

    ec2_resource = session_objects["ec2_resource"]
    ec2_client = session_objects["ec2_client"]

    # Check instance state to ensure it's started only if originally running
    instance = ec2_resource.Instance(instance_id)
    originally_running = False
    if instance.state["Name"] == "running":
        originally_running = True

    # Create snapshots and collect volume details
    volume_details = []
    for volume in instance.volumes.all():
        if not kwargs.get("re_encrypt") and volume.encrypted:
            logger.info(f"{volume.id} - skipped, already encrypted")
            continue
        device = volume.attachments[0]["Device"]
        snapshot = session_objects["ec2_resource"].create_snapshot(
            VolumeId=volume.id,
            Description=f"Pre-encryption snapshot of {volume.id}",
            TagSpecifications=[
                {
                    "ResourceType": "snapshot",
                    "Tags": [{"Key": "Name", "Value": f"source:{volume.id}"}],
                }
            ],
        )
        logger.info(f"{snapshot.id} - creating from {volume.id}")
        volume_details.append((volume, device, snapshot))

    # Wait for snapshots to complete
    for _, _, snapshot in volume_details:
        snapshot.wait_until_completed()

    # Create encrypted volumes from snapshots
    encrypted_volumes_info = []
    for volume, device, snapshot in volume_details:
        create_volume_args = {
            "SnapshotId": snapshot.id,
            "AvailabilityZone": volume.availability_zone,
            "Encrypted": True,
            "KmsKeyId": kms_key_id,
        }
        if volume.tags:
            create_volume_args["TagSpecifications"] = [
                {"ResourceType": "volume", "Tags": volume.tags}
            ]

        encrypted_volume = ec2_resource.create_volume(**create_volume_args)
        encrypted_volumes_info.append((encrypted_volume, device))
        logger.info(f"{encrypted_volume.id} - creating")

    # Wait for all encrypted volumes to be available
    encrypted_volume_ids = [vol.id for vol, _ in encrypted_volumes_info]
    waiter = ec2_client.get_waiter("volume_available")

    # Proceed only if encrypted volumes have been created
    if encrypted_volume_ids:
        waiter.wait(VolumeIds=encrypted_volume_ids)

        # Stop instance
        instance.stop()
        logger.info(f"{instance_id} - stopping")
        instance.wait_until_stopped()

        # Detach original volumes
        for volume, _, _ in volume_details:
            volume.detach_from_instance()
            logger.info(f"{volume.id} ({volume.attachments[0]['Device']}) - detaching")

        # Wait for volumes to be detached
        waiter.wait(VolumeIds=[vol.id for vol, _, _ in volume_details])

        # Attach encrypted volumes
        for encrypted_volume, device in encrypted_volumes_info:
            instance.attach_volume(VolumeId=encrypted_volume.id, Device=device)
            logger.info(
                f"{encrypted_volume.id} - attaching to {instance.id} as {device}"
            )

        # Start instance
        if originally_running:
            instance.start()
            logger.info(f"{instance_id} - starting")
            instance.wait_until_running()

        # Delete snapshots
        for _, _, snapshot in volume_details:
            snapshot.delete()
            logger.info(f"{snapshot.id} - deleted")

        logger.info("To rollback:")
        logger.info("1. Attach")
        for volume, device, _ in volume_details:
            logger.info(f" -> {volume.id} to {instance_id} as {device}")

        logger.info("2. Delete")
        for encrypted_volume, _ in encrypted_volumes_info:
            logger.info(f" -> {encrypted_volume.id}")
    else:
        logger.info("No volumes to encrypt")

    return instance.id
