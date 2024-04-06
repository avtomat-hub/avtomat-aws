import logging

from botocore.config import Config

logger = logging.getLogger(__name__)


config = Config(retries={"max_attempts": 5, "mode": "standard"})


def set_session_objects(session, region, clients=None, resources=None):
    """Set the session objects(clients and resources)."""

    session_objects = {}

    if clients:
        for client in clients:
            session_objects[f"{client}_client"] = session.client(
                client, region_name=region, config=config
            )

    if resources:
        for resource in resources:
            session_objects[f"{resource}_resource"] = session.resource(
                resource, region_name=region, config=config
            )

    return session_objects
