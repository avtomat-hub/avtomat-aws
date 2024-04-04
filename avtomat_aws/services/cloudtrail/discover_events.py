import logging
from datetime import datetime, timedelta

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "created_after": (datetime.now() - timedelta(days=90)).strftime("%Y/%m/%d"),
    "created_before": (datetime.now()).strftime("%Y/%m/%d"),
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["event"]},
    {"date_yymmdd": ["created_after", "created_before"]},
    {"cloudtrail": ["created_after", "created_before"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_events(**kwargs):
    """Discover events by name"""

    # Required parameters
    event = kwargs.pop("event")

    if kwargs.get("created_after"):
        kwargs["created_after"] = datetime.strptime(kwargs["created_after"], "%Y/%m/%d")
    if kwargs.get("created_before"):
        kwargs["created_before"] = datetime.strptime(
            kwargs["created_before"], "%Y/%m/%d"
        )

    logger.info(f"Discovering CloudTrail events for '{event}'")

    events = search_events(event, **kwargs)

    logger.info(f"{len(events)} events found")
    logger.debug(events)

    return events


def search_events(event, **kwargs):
    """Search for events"""

    session = kwargs["session"]
    region = kwargs["region"]
    created_after = kwargs.get("created_after")
    created_before = kwargs.get("created_before")

    session_objects = set_session_objects(
        session, clients=["cloudtrail"], region=region
    )
    events = []

    response = session_objects["cloudtrail_client"].lookup_events(
        LookupAttributes=[{"AttributeKey": "EventName", "AttributeValue": event}],
        StartTime=created_after,
        EndTime=created_before,
    )

    while True:
        for obj in response["Events"]:
            data = {
                "UserName": obj["Username"],
                "EventTime": obj["EventTime"].isoformat(),
                "EventName": obj["EventName"],
                "Resources": [
                    resource["ResourceName"] for resource in obj["Resources"]
                ],
            }
            events.append(data)

        if response.get("NextToken"):
            response = session_objects["cloudtrail_client"].lookup_events(
                LookupAttributes=[
                    {"AttributeKey": "EventName", "AttributeValue": event}
                ],
                StartTime=created_after,
                EndTime=created_before,
                NextToken=response["NextToken"],
            )
        else:
            break

    return events
