import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"re_encrypt": False, "region": None, "debug": False, "silent": False}
RULES = [{"required": ["volume_id", "kms_key_id"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def encrypt_volume(**kwargs):
    """Encrypt an EBS volume with a KMS key"""

    # Required parameters
    volume_id = kwargs.pop("volume_id")
    kms_key_id = kwargs.pop("kms_key_id")

    session_objects = set_session_objects(
        kwargs.get("session"),
        clients=["ec2"],
        resources=["ec2"],
        region=kwargs["region"],
    )

    logger.info(f"{volume_id} - encrypting with {kms_key_id}")

    # Create snapshot
    volume = session_objects["ec2_resource"].Volume(volume_id)

    if not kwargs.get("re_encrypt") and volume.encrypted:
        logger.info(f"{volume_id} - skipped, already encrypted")
        logger.info("Done")
        return volume_id

    attached = False
    if volume.state == "in-use":
        attached = True
        instance_id = volume.attachments[0]["InstanceId"]
        device = volume.attachments[0]["Device"]
        instance = session_objects["ec2_resource"].Instance(instance_id)

        # Check instance state to ensure it's started only if originally running
        originally_running = False
        if instance.state["Name"] == "running":
            originally_running = True

    snapshot = session_objects["ec2_resource"].create_snapshot(
        VolumeId=volume_id,
        Description=f"Pre-encryption snapshot of {volume_id}",
        TagSpecifications=[
            {
                "ResourceType": "snapshot",
                "Tags": [{"Key": "Name", "Value": f"source:{volume_id}"}],
            }
        ],
    )
    snapshot.load()
    logger.info(f"{snapshot.id} - creating")
    snapshot.wait_until_completed()

    # Create encrypted volume from snapshot
    encrypted_volume = session_objects["ec2_resource"].create_volume(
        SnapshotId=snapshot.id,
        AvailabilityZone=volume.availability_zone,
        Encrypted=True,
        KmsKeyId=kms_key_id,
    )
    logger.info(f"{encrypted_volume.id} - creating")
    waiter = session_objects["ec2_client"].get_waiter("volume_available")
    waiter.wait(VolumeIds=[encrypted_volume.id])

    # Copy tags from original volume to encrypted volume
    original_tags = volume.tags
    if original_tags is None:
        original_tags = []
    if original_tags:
        session_objects["ec2_client"].create_tags(
            Resources=[encrypted_volume.id], Tags=original_tags
        )
    logger.info(f"{encrypted_volume.id} - tags copied from {volume_id}")

    # If original volume is in use, swap volumes
    if attached:
        instance.stop()
        logger.info(f"{instance_id} - stopping")
        instance.wait_until_stopped()

        logger.info(f"{volume_id} ({device}) - detaching")
        volume.detach_from_instance()
        waiter = session_objects["ec2_client"].get_waiter("volume_available")
        waiter.wait(VolumeIds=[volume_id])

        logger.info(f"{encrypted_volume.id} - attaching to {instance_id} as {device}")
        instance.attach_volume(VolumeId=encrypted_volume.id, Device=device)

        if originally_running:
            instance.start()
            logger.info(f"{instance_id} - starting")
            instance.wait_until_running()

    # Cleanup
    snapshot.delete()
    logger.info(f"{snapshot.id} - deleted")

    # Rollback instructions
    if attached:
        logger.info(
            f"To rollback, attach {volume_id} to {instance_id} as {device} and delete {encrypted_volume.id}"
        )
    else:
        logger.info(f"To rollback, delete {encrypted_volume.id}")

    return encrypted_volume.id
