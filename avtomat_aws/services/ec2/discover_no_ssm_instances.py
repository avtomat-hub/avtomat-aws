import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"instance_ids": [], "region": None, "debug": False, "silent": False}


@validate(DEFAULTS)
@set_logger()
@authenticate()
def discover_no_ssm_instances(**kwargs):
    """Discover EC2 instances without SSM enabled"""

    session_objects = set_session_objects(
        kwargs["session"],
        clients=["ec2", "ssm"],
        resources=["ec2"],
        region=kwargs["region"],
    )

    logger.info(f"Discovering instances without SSM enabled")

    ssm_instances = []
    response = session_objects["ssm_client"].describe_instance_information(
        InstanceInformationFilterList=[{"key": "PingStatus", "valueSet": ["Online"]}]
    )
    while True:
        for instance in response["InstanceInformationList"]:
            ssm_instances.append(instance["InstanceId"])

        if response.get("NextToken"):
            response = session_objects["ssm_client"].describe_instance_information(
                InstanceInformationFilterList=[
                    {"key": "PingStatus", "valueSet": ["Online"]}
                ],
                NextToken=response["NextToken"],
            )
        else:
            break

    no_ssm_instances = []
    for instance in session_objects["ec2_resource"].instances.filter(
        InstanceIds=kwargs["instance_ids"]
    ):
        if instance.id not in ssm_instances:
            no_ssm_instances.append(instance.id)

    logger.info(f"{len(no_ssm_instances)} instances found")
    logger.debug(no_ssm_instances)

    return no_ssm_instances
