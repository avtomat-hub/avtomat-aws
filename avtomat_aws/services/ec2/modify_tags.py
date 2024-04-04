import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "create": False,
    "delete": False,
    "dynamic_tags": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["resource_ids", "tags"]},
    {"at_least_one": ["create", "delete"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def modify_tags(**kwargs):
    """Create or delete tags for EC2 resources"""

    if not kwargs.get("delete"):
        for tag in kwargs["tags"]:
            if "=" not in tag:
                raise ValueError(
                    f"Tag '{tag}' not in Key=Value format."
                )  # Needs a validation rule

    # Change tags into the correct format
    # Needs better handling
    formatted_tags = []
    for tag in kwargs["tags"]:
        if "=" in tag:
            key, value = tag.split("=", 1)
            formatted_tags.append({"Key": key, "Value": value})
        else:
            key = tag
            formatted_tags.append({"Key": key})
    kwargs["tags"] = formatted_tags

    # Required parameters
    resource_ids = kwargs.pop("resource_ids")
    tags = kwargs.pop("tags")

    if not resource_ids:
        logger.info("No resources to modify tags for")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["ec2"], region=kwargs["region"]
    )

    if kwargs.get("create"):
        logger.info(f"Creating tags for resources")
    elif kwargs.get("delete"):
        logger.info(f"Deleting tags for resources")

    if kwargs.get("dynamic_tags"):
        failed_resources = dynamic_tags(tags, resource_ids, session_objects, **kwargs)
    else:
        failed_resources = static_tags(tags, resource_ids, session_objects, **kwargs)

    if failed_resources:
        logger.info(f"{len(failed_resources)} resources failed tag modification")
    else:
        logger.info("Success")
    logger.debug(failed_resources)

    return failed_resources


def dynamic_tags(tags, resource_ids, session_objects, **kwargs):
    """Create tags in dynamic mode, uses an API call per resource"""

    failed_resources = []
    for resource_id in resource_ids:
        # Replace {resource_id} with the actual resource_id
        dynamic_tags = []
        for tag in tags:
            dynamic_tags.append(
                {
                    "Key": tag["Key"].replace("{resource_id}", resource_id),
                    "Value": tag["Value"].replace("{resource_id}", resource_id),
                }
            )
        try:
            if kwargs.get("create"):
                session_objects["ec2_client"].create_tags(
                    Resources=[resource_id], Tags=dynamic_tags
                )
            elif kwargs.get("delete"):
                session_objects["ec2_client"].delete_tags(
                    Resources=[resource_id], Tags=dynamic_tags
                )
        except Exception as e:
            logger.error(f"Failed to modify tags for resource {resource_id} - {e}")
            failed_resources.append(resource_id)
            continue

    return failed_resources


def static_tags(tags, resource_ids, session_objects, **kwargs):
    """Create tags in static mode, uses an API call per 200 resources"""

    failed_resources = []
    if len(resource_ids) > 200:
        # Split the resources into chunks of 200
        chunks = [resource_ids[i : i + 200] for i in range(0, len(resource_ids), 200)]
        for chunk in chunks:
            try:
                if kwargs.get("create"):
                    session_objects["ec2_client"].create_tags(
                        Resources=chunk, Tags=tags
                    )
                elif kwargs.get("delete"):
                    session_objects["ec2_client"].delete_tags(
                        Resources=chunk, Tags=tags
                    )
            except Exception as e:
                logger.error(f"Failed to modify tags for resources for a chunk - {e}")
                failed_resources.extend(chunk)
                continue
    else:
        try:
            if kwargs.get("create"):
                session_objects["ec2_client"].create_tags(
                    Resources=resource_ids, Tags=tags
                )
            elif kwargs.get("delete"):
                session_objects["ec2_client"].delete_tags(
                    Resources=resource_ids, Tags=tags
                )
        except Exception as e:
            logger.error(f"Failed to modify tags for resources - {e}")
            failed_resources.extend(resource_ids)

    return failed_resources
