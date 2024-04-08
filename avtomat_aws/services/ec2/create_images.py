import logging
import uuid

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"reboot": False, "region": None, "debug": False, "silent": False}
RULES = [{"required": ["instance_ids"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def create_images(**kwargs):
    """Create EC2 images (AMI)"""

    # Required parameters
    instance_ids = kwargs.pop("instance_ids")

    if not instance_ids:
        logger.info("No instances to create images from")
        return []

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info(f"Creating images")

    images = []
    failed = []
    for instance_id in instance_ids:
        try:
            instance = session_objects["ec2_resource"].Instance(instance_id)
            # Generate random uuid as image names must be unique
            uuid_str = str(uuid.uuid4())
            image = instance.create_image(
                Name=f"source_{instance_id}_{uuid_str}",
                Description=f"Image of {instance_id}",
                NoReboot=not kwargs["reboot"],
                TagSpecifications=[
                    {
                        "ResourceType": "image",
                        "Tags": get_tags(instance_id, session_objects),
                    }
                ],
            )
            logger.info(f"{instance_id} - creating {image.id}")
            images.append(image.id)
        except Exception as e:
            failed.append(instance_id)
            logger.error(f"{instance_id} - failed to create image - {e}")
            continue

    # An error is returned after 10 minutes of waiting. Can be modified with the WaiterConfig.
    for image in images:
        image = session_objects["ec2_resource"].Image(image)
        image.wait_until_exists(Filters=[{"Name": "state", "Values": ["available"]}])

    logger.info(f"{len(images)} images created")
    if failed:
        logger.warning(f"{len(failed)} instances failed the image creation process")
        logger.debug(failed)

    return images


def get_tags(instance_id, session_objects):
    """Get tags from an EC2 instance"""
    instance = session_objects["ec2_resource"].Instance(instance_id)
    tags = instance.tags
    return tags
