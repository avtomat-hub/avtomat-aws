import logging
from datetime import datetime, timedelta

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "events": [],
    "created_after": (datetime.now() - timedelta(days=90)).strftime("%Y/%m/%d"),
    "created_before": (datetime.now()).strftime("%Y/%m/%d"),
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["resource_id"]},
    {"date_yymmdd": ["created_after", "created_before"]},
    {"cloudtrail": ["created_after", "created_before"]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_resource_events(**kwargs):
    """Discover events for a specific resource"""

    # Required parameters
    resource_id = kwargs.pop("resource_id")

    if kwargs.get("created_after"):
        kwargs["created_after"] = datetime.strptime(kwargs["created_after"], "%Y/%m/%d")
    if kwargs.get("created_before"):
        kwargs["created_before"] = datetime.strptime(
            kwargs["created_before"], "%Y/%m/%d"
        )

    logger.info(f"Discovering CloudTrail events for resource '{resource_id}'")

    unfiltered_events = search_events(resource_id, **kwargs)
    events = filter_events(unfiltered_events, **kwargs)

    logger.info(f"{len(events)} events found")
    logger.debug(events)

    return events


def search_events(resource_id, **kwargs):
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
        LookupAttributes=[
            {"AttributeKey": "ResourceName", "AttributeValue": resource_id}
        ],
        StartTime=created_after,
        EndTime=created_before,
    )

    while True:
        for event in response["Events"]:
            data = {
                "UserName": event["Username"],
                "EventTime": event["EventTime"].isoformat(),
                "EventName": event["EventName"],
                "Resources": [
                    resource["ResourceName"] for resource in event["Resources"]
                ],
            }
            events.append(data)

        if response.get("NextToken"):
            response = session_objects["cloudtrail_client"].lookup_events(
                LookupAttributes=[
                    {"AttributeKey": "ResourceName", "AttributeValue": resource_id}
                ],
                StartTime=created_after,
                EndTime=created_before,
                NextToken=response["NextToken"],
            )
        else:
            break

    return events


def filter_events(unfiltered_events, **kwargs):
    """Filter events based on specified criteria"""

    events = kwargs.get("events")
    filtered_events = unfiltered_events

    if events:
        logger.debug(f"Filtering for events: {events}")
        filtered_events = [
            event for event in filtered_events if event["EventName"] in events
        ]

    return filtered_events
