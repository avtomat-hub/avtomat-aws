import logging
from datetime import datetime, timezone

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "prefix": "",
    "modified_before": None,
    "modified_after": None,
    "name_only": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["bucket"]},
    {"date_yymmdd": ["modified_before", "modified_after"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_objects(**kwargs):
    """Discover objects in an S3 bucket"""

    # Required parameters
    bucket = kwargs.pop("bucket")

    if kwargs.get("modified_before"):
        kwargs["modified_before"] = datetime.strptime(
            kwargs["modified_before"], "%Y/%m/%d"
        ).replace(tzinfo=timezone.utc)
    if kwargs.get("modified_after"):
        kwargs["modified_after"] = datetime.strptime(
            kwargs["modified_after"], "%Y/%m/%d"
        ).replace(tzinfo=timezone.utc)

    session_objects = set_session_objects(
        kwargs["session"], resources=["s3"], region=kwargs["region"]
    )

    if kwargs.get("prefix"):
        logger.info(
            f"Discovering objects in '{bucket}' with prefix '{kwargs['prefix']}'"
        )
    else:
        logger.info(f"Discovering objects in '{bucket}'")

    response = (
        session_objects["s3_resource"]
        .Bucket(bucket)
        .objects.filter(Prefix=kwargs["prefix"])
    )
    objects = filter_objects(response, **kwargs)

    logger.info(f"{len(objects)} objects found")
    logger.debug(objects)

    return objects


def filter_objects(response, **kwargs):
    """Filter objects based on additional criteria"""

    filtered_objects = response

    if kwargs.get("modified_before"):
        filtered_objects = [
            obj
            for obj in filtered_objects
            if obj.last_modified < kwargs["modified_before"]
        ]

    if kwargs.get("modified_after"):
        filtered_objects = [
            obj
            for obj in filtered_objects
            if obj.last_modified > kwargs["modified_after"]
        ]

    if kwargs.get("name_only"):
        filtered_objects = [obj.key.split("/")[-1] for obj in filtered_objects]
    else:
        filtered_objects = [obj.key for obj in filtered_objects]

    return filtered_objects
