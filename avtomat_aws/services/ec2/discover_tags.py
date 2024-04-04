import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "existing": False,
    "missing": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["resource_types", "tags"]},
    {
        "choice": [
            {
                "resource_types": [
                    "image",
                    "instance",
                    "internet_gateway",
                    "key_pair",
                    "network_acl",
                    "route_table",
                    "security_group",
                    "snapshot",
                    "subnet",
                    "volume",
                    "vpc",
                ]
            },
        ]
    },
    {"at_most_one": ["existing", "missing"]},
    {"at_least_one": ["existing", "missing"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_tags(**kwargs):
    """Discover specific tags that exist on EC2 resources"""

    # Required parameters
    resource_types = kwargs.pop("resource_types")
    tags = kwargs.pop("tags")

    # Convert 'tags' from ['Key=Value', 'Key', ...] format to a list of tuples [(Key, Value), (Key, None), ...]
    tag_tuples = []
    for tag in tags:
        if "=" in tag:
            key, value = tag.split("=", 1)
            tag_tuples.append((key, value))
        else:
            tag_tuples.append((tag, None))

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    if kwargs.get("existing"):
        logger.info(f"Discovering resources with tags: {tags}")
    elif kwargs.get("missing"):
        logger.info(f"Discovering resources without tags: {tags}")

    resources = []
    if "image" in resource_types:
        response = session_objects["ec2_resource"].images.filter(Owners=["self"])
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "instance" in resource_types:
        response = session_objects["ec2_resource"].instances.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "internet_gateway" in resource_types:
        response = session_objects["ec2_resource"].internet_gateways.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "key_pair" in resource_types:
        response = session_objects["ec2_resource"].key_pairs.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "network_acl" in resource_types:
        response = session_objects["ec2_resource"].network_acls.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "route_table" in resource_types:
        response = session_objects["ec2_resource"].route_tables.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "security_group" in resource_types:
        response = session_objects["ec2_resource"].security_groups.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "snapshot" in resource_types:
        response = session_objects["ec2_resource"].snapshots.filter(OwnerIds=["self"])
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "subnet" in resource_types:
        response = session_objects["ec2_resource"].subnets.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "volume" in resource_types:
        response = session_objects["ec2_resource"].volumes.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))
    if "vpc" in resource_types:
        response = session_objects["ec2_resource"].vpcs.all()
        resources.extend(search_collections(response, tag_tuples, **kwargs))

    logger.info(f"{len(resources)} resources found")
    logger.debug(resources)

    return resources


def search_collections(response, tags, **kwargs):
    """Iterate through resources in the response and return ones that have or don't have supplied tags"""

    missing = kwargs.get("missing")
    existing = kwargs.get("existing")

    resources = []
    for resource in response:
        resource_tags = {
            tag["Key"]: tag.get("Value", None)
            for tag in getattr(resource, "tags") or []
        }
        match = False

        if missing:
            match = any(
                (
                    key not in resource_tags
                    or (value is not None and resource_tags[key] != value)
                )
                for key, value in tags
            )

        elif existing:
            match = all(
                key in resource_tags and (value is None or resource_tags[key] == value)
                for key, value in tags
            )

        if match:
            try:
                resources.append(resource.id)
            except AttributeError:
                resources.append(resource.name)

    return resources
