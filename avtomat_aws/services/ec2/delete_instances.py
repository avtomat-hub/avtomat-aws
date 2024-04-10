import logging
import time
import uuid

from botocore.exceptions import ClientError, WaiterError

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "include": None,
    "final_image": False,
    "disable_protections": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["instance_ids"]},
    {
        "choice": [
            {"include": ["volume", "image", "snapshot"]},
        ]
    },
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_instances(**kwargs):
    """Delete EC2 instances"""

    # Required parameters
    instance_ids = kwargs.pop("instance_ids")

    if not instance_ids:
        logger.info("No instances to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )
    failed = {"Instances": [], "Volumes": [], "Images": [], "Snapshots": []}

    # Get instance objects
    instances = []
    for instance_id in instance_ids:
        try:
            instance = session_objects["ec2_resource"].Instance(instance_id)
            useless = instance.state  # Check if instance exists
            instances.append(instance)
        except Exception as e:
            failed["Instances"].append(instance_id)
            logger.error(f"{instance_id} - failed to discover instance")
            continue

    # Gatekeeper: If no instances remain, return early
    if not instances:
        return failed

    # Discover associated resources before deletion
    associated_resources = {"Volumes": [], "Images": [], "Snapshots": []}
    if kwargs.get("include"):
        logger.info(f"Discovering associated resources: {kwargs.get('include')}")
        if "volume" in kwargs.get("include"):
            associated_resources["Volumes"] = discover_volumes(instances)
        if "image" in kwargs.get("include"):
            associated_resources["Images"], associated_resources["Snapshots"] = (
                discover_images(instances, session_objects["ec2_resource"])
            )
        if "snapshot" in kwargs.get("include"):
            if not associated_resources[
                "Volumes"
            ]:  # If volume deletion wasn't requested (we still need volumes for snapshots)
                associated_resources["Volumes"] = discover_volumes(instances)
            associated_resources["Snapshots"] += discover_snapshots(
                associated_resources["Volumes"], session_objects["ec2_resource"]
            )  # We append instead of assign to avoid overwriting snapshots associated with images
            associated_resources["Snapshots"] = list(
                set(associated_resources["Snapshots"])
            )  # Deduplicate

    if kwargs.get("disable_protections"):
        logger.info("Disabling API protections")
        disable_protections(instances)

    running_instances_to_stop = []
    logger.info("Stopping any running instances")
    for instance in instances:  # First concurrently stop all running instances.
        if instance.state["Name"] == "running":
            logger.info(f"{instance.id} - running, stopping before deletion")
            instance.stop()
            running_instances_to_stop.append(instance)
    for (
        instance
    ) in (
        running_instances_to_stop
    ):  # Then wait for them to stop. Avoids waiting per instance.
        instance.wait_until_stopped()

    images_to_wait = []
    if kwargs.get("final_image"):
        logger.info("Creating images before deletion")
        for instance in instances[:]:  # Iterate over a shallow copy
            try:
                # Generate random uuid as image names must be unique
                uuid_str = str(uuid.uuid4())
                image = instance.create_image(
                    Name=f"source_{instance.id}_{uuid_str}",
                    Description=f"Pre-deletion image of {instance.id}",
                    NoReboot=True,
                    TagSpecifications=[
                        {
                            "ResourceType": "image",
                            "Tags": instance.tags,
                        }
                    ],
                )
                logger.info(f"{instance.id} - creating {image.id}")
                images_to_wait.append((image, instance, uuid_str))
            except Exception as e:
                failed["Instances"].append(instance.id)
                instances.remove(instance)  # Modify the original list
                logger.error(
                    f"{instance.id} - failed to create image, will not delete - {e}"
                )
                continue

    # Gatekeeper: If no instances remain, return early
    if not instances:
        return failed

    for image, instance, _ in images_to_wait:
        try:
            image.wait_until_exists(
                Filters=[{"Name": "state", "Values": ["available"]}]
            )
        except WaiterError as e:
            failed["Instances"].append(instance.id)
            instances.remove(instance)
            logger.error(
                f"{instance.id} - failed to create image, will not delete - {e}"
            )
            continue

    # Gatekeeper: If no instances remain, return early
    if not instances:
        return failed

    logger.info(f"Deleting instances")
    for instance in instances[:]:  # Iterate over a shallow copy
        try:
            instance.terminate()
            logger.info(f"{instance.id} - deleted")
        except Exception as e:
            failed["Instances"].append(instance.id)
            instances.remove(instance)  # Modify the original list
            logger.error(f"{instance.id} - failed to delete - {e}")
            if kwargs.get(
                "final_image"
            ):  # Cleanup newly created image if deletion fails
                for image, _, uuid_str in images_to_wait:
                    if image.name == f"source_{instance.id}_{uuid_str}":
                        snapshots = discover_image_snapshots(
                            image, session_objects["ec2_resource"]
                        )
                        image.deregister()
                        delete_snapshots(snapshots, cleanup_final_image=True)
                        logger.warning(f"{instance.id} - cleaned up {image.id}")
            continue

    # Gatekeeper: If no instances remain, return early
    if not instances:
        return failed

    time.sleep(
        5
    )  # Wait for a few seconds before attempting to delete associated resources

    volumes_counter = 0
    images_counter = 0
    snapshots_counter = 0
    if kwargs.get("include"):
        logger.info(f"Deleting associated resources: {kwargs.get('include')}")
        if "volume" in kwargs.get("include"):
            volumes_counter, failed["Volumes"] = delete_volumes(
                associated_resources["Volumes"]
            )
        if "image" in kwargs.get("include"):
            images_counter, failed["Images"] = delete_images(
                associated_resources["Images"]
            )
        if "image" in kwargs.get("include") or "snapshot" in kwargs.get("include"):
            snapshots_counter, failed["Snapshots"] = delete_snapshots(
                associated_resources["Snapshots"]
            )

        # Provide a summary of deleted resources
        logger.info(f"{len(instances)} instances deleted")
        logger.info(f"{volumes_counter} volumes deleted")
        logger.info(f"{images_counter} images deleted")
        logger.info(f"{snapshots_counter} snapshots deleted")

        if failed["Instances"]:
            logger.warning(f"{len(failed['Instances'])} instances failed to delete")
            logger.debug(failed["Instances"])
        if failed["Volumes"]:
            logger.warning(f"{len(failed['Volumes'])} volumes failed to delete")
            logger.debug(failed["Volumes"])
        if failed["Images"]:
            logger.warning(f"{len(failed['Images'])} images failed to delete")
            logger.debug(failed["Images"])
        if failed["Snapshots"]:
            logger.warning(f"{len(failed['Snapshots'])} snapshots failed to delete")
            logger.debug(failed["Snapshots"])

    return failed


def delete_volumes(volumes):
    """Delete all volumes associated with an instance"""
    counter = 0
    failed = []
    for volume in volumes:
        try:
            volume.delete()
            counter += 1
            logger.info(f"{volume.id} - deleted")
        except Exception as e:
            failed.append(volume.id)
            logger.error(f"{volume.id} - failed to delete - {e}")
            continue
    return counter, failed


def delete_images(images):
    """Delete all images associated with an instance"""
    counter = 0
    failed = []
    for image in images:
        try:
            image.deregister()
            counter += 1
            logger.info(f"{image.id} - deleted")
        except Exception as e:
            failed.append(image.id)
            logger.error(f"{image.id} - failed to delete - {e}")
            continue
    return counter, failed


def delete_snapshots(snapshots, cleanup_final_image=False):
    """Delete all snapshots associated with an image"""
    counter = 0
    failed = []
    for snapshot in snapshots:
        try:
            snapshot.delete()
            counter += 1
            if (
                not cleanup_final_image
            ):  # Don't log extra messages if cleaning up a final image
                logger.info(f"{snapshot.id} - deleted")
        except Exception as e:
            failed.append(snapshot.id)
            logger.error(f"{snapshot.id} - failed to delete - {e}")
            continue
    return counter, failed


def discover_volumes(instances):
    """Discover volumes associated with instances"""
    volumes = []
    for instance in instances:
        volumes += instance.volumes.all()
    return volumes


def discover_images(instances, ec2_resource):
    """Discover images (and their underlying snapshots) associated with instances"""
    instance_ids = [instance.id for instance in instances]
    images = []
    for image in ec2_resource.images.filter(
        Owners=["self"],
        Filters=[{"Name": "source-instance-id", "Values": instance_ids}],
    ):
        images.append(image)
    snapshots = []
    for image in images:
        if image.state == "available":
            snapshots += discover_image_snapshots(image, ec2_resource)
        else:
            logger.warning(
                f"{image.id} - not fully available, will skip snapshot deletion"
            )
    return images, snapshots


def discover_snapshots(volumes, ec2_resource):
    """Discover snapshots associated with volumes"""
    volume_ids = [volume.id for volume in volumes]
    snapshots = []
    for snapshot in ec2_resource.snapshots.filter(
        OwnerIds=["self"], Filters=[{"Name": "volume-id", "Values": volume_ids}]
    ):
        snapshots.append(snapshot)
    return snapshots


def discover_image_snapshots(image, ec2_resource):
    """Discover snapshots associated with images"""
    snapshots = []
    for snapshot_id in image.block_device_mappings:
        try:
            snapshot = ec2_resource.Snapshot(snapshot_id["Ebs"]["SnapshotId"])
            snapshots.append(snapshot)
        except Exception as e:
            logger.error(f"{image.id} - failed to discover snapshots - {e}")
            continue
    return snapshots


def disable_protections(instances):
    """Disable termination and stop protections for instances"""
    for instance in instances:
        try:
            instance.modify_attribute(DisableApiTermination={"Value": False})
            instance.modify_attribute(DisableApiStop={"Value": False})
            logger.info(f"{instance.id} - api protections disabled")
        except Exception as e:
            logger.error(f"{instance.id} - failed to disable api protections - {e}")
