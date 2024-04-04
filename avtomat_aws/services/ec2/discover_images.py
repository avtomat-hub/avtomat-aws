import logging
from datetime import datetime, timezone

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "image_ids": [],
    "public": False,
    "exclude_aws_backup": False,
    "created_before": None,
    "created_after": None,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [{"date_yymmdd": ["created_before", "created_after"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_images(**kwargs):
    """Discover images based on provided criteria"""

    if kwargs.get("created_before"):
        kwargs["created_before"] = datetime.strptime(
            kwargs["created_before"], "%Y/%m/%d"
        )
    if kwargs.get("created_after"):
        kwargs["created_after"] = datetime.strptime(kwargs["created_after"], "%Y/%m/%d")

    logger.info("Discovering images")

    filters = build_filters(**kwargs)
    images = search_images(filters, **kwargs)

    logger.info(f"{len(images)} images found")
    logger.debug(images)

    return images


def build_filters(**kwargs):
    """Construct filters"""

    image_ids = kwargs.get("image_ids")
    public = kwargs.get("public")
    exclude_aws_backup = kwargs.get("exclude_aws_backup")

    filters = []
    if public:
        logger.debug("Filtering for public images")
        filters.append({"Name": "is-public", "Values": ["true"]})
    if exclude_aws_backup:
        logger.debug("Filtering out AWS Backup images")
    if image_ids:
        logger.debug(f"Filtering for images: {image_ids}")

    return filters


def search_images(filters, **kwargs):
    """Search for images in specified region"""

    session = kwargs["session"]
    region = kwargs["region"]
    image_ids = kwargs.get("image_ids")
    created_before = kwargs.get("created_before")
    created_after = kwargs.get("created_after")
    exclude_aws_backup = kwargs.get("exclude_aws_backup")

    session_objects = set_session_objects(session, resources=["ec2"], region=region)
    images = []

    response = session_objects["ec2_resource"].images.filter(
        Filters=filters, Owners=["self"], ImageIds=image_ids
    )

    for image in response:
        creation_date = datetime.fromisoformat(
            image.creation_date.replace("Z", "+00:00")
        )
        if created_before and creation_date > created_before.replace(
            tzinfo=timezone.utc
        ):
            continue
        if created_after and creation_date < created_after.replace(tzinfo=timezone.utc):
            continue
        if exclude_aws_backup and any(
            tag["Key"].startswith("aws:backup") for tag in (image.tags or [])
        ):
            continue
        images.append(image.id)

    return images
