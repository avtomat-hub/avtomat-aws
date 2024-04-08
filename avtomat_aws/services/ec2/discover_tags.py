import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.format_tags import format_tags
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

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    if kwargs.get("existing"):
        logger.info(f"Discovering resources with tags: {tags}")
    elif kwargs.get("missing"):
        logger.info(f"Discovering resources without tags: {tags}")

    formatted_tags = format_tags(tags)
    resources = []
    if "image" in resource_types:
        response = session_objects["ec2_resource"].images.filter(Owners=["self"])
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "instance" in resource_types:
        response = session_objects["ec2_resource"].instances.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "internet_gateway" in resource_types:
        response = session_objects["ec2_resource"].internet_gateways.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "key_pair" in resource_types:
        response = session_objects["ec2_resource"].key_pairs.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "network_acl" in resource_types:
        response = session_objects["ec2_resource"].network_acls.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "route_table" in resource_types:
        response = session_objects["ec2_resource"].route_tables.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "security_group" in resource_types:
        response = session_objects["ec2_resource"].security_groups.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "snapshot" in resource_types:
        response = session_objects["ec2_resource"].snapshots.filter(OwnerIds=["self"])
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "subnet" in resource_types:
        response = session_objects["ec2_resource"].subnets.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "volume" in resource_types:
        response = session_objects["ec2_resource"].volumes.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))
    if "vpc" in resource_types:
        response = session_objects["ec2_resource"].vpcs.all()
        resources.extend(search_collections(response, formatted_tags, **kwargs))

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
                    tag["Key"] not in resource_tags
                    or (
                        tag.get("Value") is not None
                        and resource_tags[tag["Key"]] != tag["Value"]
                    )
                )
                for tag in tags
            )

        elif existing:
            match = all(
                tag["Key"] in resource_tags
                and (
                    tag.get("Value") is None
                    or resource_tags[tag["Key"]] == tag["Value"]
                )
                for tag in tags
            )

        if match:
            try:
                resources.append(resource.id)
            except AttributeError:
                resources.append(resource.name)

    return resources
