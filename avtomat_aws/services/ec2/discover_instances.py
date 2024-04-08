import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.format_tags import format_tags
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "states": ["running", "stopped", "pending", "stopping"],
    "tags": [],
    "instance_ids": [],
    "invert": False,
    "os": None,
    "public": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {
        "choice": [
            {
                "states": [
                    "pending",
                    "running",
                    "shutting-down",
                    "terminated",
                    "stopping",
                    "stopped",
                ]
            },
            {"os": ["linux", "windows"]},
        ]
    }
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_instances(**kwargs):
    """Discover EC2 instances based on provided criteria"""

    session_objects = set_session_objects(
        kwargs["session"], resources=["ec2"], region=kwargs["region"]
    )

    logger.info("Discovering instances")

    filters = build_filters(**kwargs)
    instances = search_instances(filters, session_objects, **kwargs)

    if kwargs.get("invert"):
        logger.debug("Inverting the results")
        all_instances = session_objects["ec2_resource"].instances.all()
        instances = [
            instance.id for instance in all_instances if instance.id not in instances
        ]

    logger.info(f"{len(instances)} instances found")
    logger.debug(instances)

    return instances


def build_filters(**kwargs):
    """Construct filters"""

    tags = kwargs.get("tags")
    public = kwargs.get("public")
    states = kwargs.get("states")
    instance_ids = kwargs.get("instance_ids")

    filters = []
    filters.append({"Name": "instance-state-name", "Values": states})

    if tags:
        logger.debug(f"Filtering for tags: {tags}")
        formatted_tags = format_tags(tags)
        for tag in formatted_tags:
            if tag.get("Key") and tag.get("Value"):
                filters.append({"Name": f"tag:{tag['Key']}", "Values": [tag["Value"]]})
            else:
                filters.append({"Name": "tag-key", "Values": [tag["Key"]]})

    if public:
        logger.debug("Filtering for public instances")
        filters.append({"Name": "ip-address", "Values": ["*"]})

    if instance_ids:
        logger.debug(f"Filtering for instances: {instance_ids}")

    if kwargs.get("os") and kwargs["os"].lower() == "windows":
        logger.debug(f"Filtering for OS: {kwargs['os']}")
        filters.append({"Name": "platform", "Values": ["windows"]})

    return filters


def search_instances(filters, session_objects, **kwargs):
    """Search for instances in specified region"""

    response = session_objects["ec2_resource"].instances.filter(
        Filters=filters, InstanceIds=kwargs["instance_ids"]
    )
    instances = [instance.id for instance in response]

    if kwargs.get("os") and kwargs["os"].lower() == "linux":
        windows_filters = [{"Name": "platform", "Values": ["windows"]}]
        response = session_objects["ec2_resource"].instances.filter(
            Filters=windows_filters, InstanceIds=kwargs["instance_ids"]
        )
        windows_instances = [instance.id for instance in response]
        instances = [id for id in instances if id not in windows_instances]

    return instances
