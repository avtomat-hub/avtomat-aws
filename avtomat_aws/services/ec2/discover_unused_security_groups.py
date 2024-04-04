import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}


@validate(DEFAULTS)
@set_logger()
@authenticate()
def discover_unused_security_groups(**kwargs):
    """Discover unused security groups"""

    session = kwargs["session"]
    region = kwargs["region"]

    logger.info("Discovering unused security groups")

    all_sgs = list_all_sgs(session, region)

    attached_sgs = set()
    attached_sgs.update(list_eni_attached_sgs(session, region))
    attached_sgs.update(list_ec2_attached_sgs(session, region))
    attached_sgs.update(list_rds_attached_sgs(session, region))
    attached_sgs.update(list_elb_attached_sgs(session, region))
    attached_sgs.update(list_elbv2_attached_sgs(session, region))
    attached_sgs.update(list_lambda_attached_sgs(session, region))
    attached_sgs.update(list_redshift_attached_sgs(session, region))
    attached_sgs.update(list_elasticache_attached_sgs(session, region))
    attached_sgs.update(list_emr_attached_sgs(session, region))
    attached_sgs.update(list_ecs_attached_sgs(session, region))
    attached_sgs.update(list_neptune_attached_sgs(session, region))
    attached_sgs.update(
        list_opensearch_attached_sgs(session, region)
    )  # No pagination support
    attached_sgs.update(list_msk_attached_sgs(session, region))

    unattached_sgs = list(all_sgs - attached_sgs)

    logger.info(f"{len(unattached_sgs)} unattached security groups found")
    logger.debug(unattached_sgs)

    return unattached_sgs


def list_all_sgs(session, region):
    """Return all security groups"""

    session_objects = set_session_objects(session, clients=["ec2"], region=region)
    sgs = set()

    response = session_objects["ec2_client"].describe_security_groups(MaxResults=500)

    if response:
        for sg in response["SecurityGroups"]:
            sgs.add(sg["GroupId"])

    while "NextToken" in response:
        response = session_objects["ec2_client"].describe_security_groups(
            MaxResults=500, NextToken=response["NextToken"]
        )
        for sg in response["SecurityGroups"]:
            sgs.add(sg["GroupId"])

    return sgs


def list_eni_attached_sgs(session, region):
    """Return security groups attached to ENIs"""

    session_objects = set_session_objects(session, clients=["ec2"], region=region)
    sgs = set()

    logger.info("Service: ENI")
    response = session_objects["ec2_client"].describe_network_interfaces(MaxResults=250)

    if response:
        for eni in response["NetworkInterfaces"]:
            for sg in eni.get("Groups", []):
                sgs.add(sg["GroupId"])

    while "NextToken" in response:
        response = session_objects["ec2_client"].describe_network_interfaces(
            MaxResults=250, NextToken=response["NextToken"]
        )
        for eni in response["NetworkInterfaces"]:
            for sg in eni.get("Groups", []):
                sgs.add(sg["GroupId"])

    return sgs


def list_ec2_attached_sgs(session, region):
    """Return security groups attached to EC2 instances"""

    session_objects = set_session_objects(session, clients=["ec2"], region=region)
    sgs = set()

    logger.info("Service: EC2")
    response = session_objects["ec2_client"].describe_instances(MaxResults=250)

    if response:
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                for sg in instance["SecurityGroups"]:
                    sgs.add(sg["GroupId"])

    while "NextToken" in response:
        response = session_objects["ec2_client"].describe_instances(
            MaxResults=250, NextToken=response["NextToken"]
        )
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                for sg in instance["SecurityGroups"]:
                    sgs.add(sg["GroupId"])

    return sgs


def list_rds_attached_sgs(session, region):
    """Return security groups attached to RDS instances"""

    session_objects = set_session_objects(session, clients=["rds"], region=region)
    sgs = set()

    logger.info("Service: RDS")
    response = session_objects["rds_client"].describe_db_instances(MaxRecords=100)

    if response:
        for instance in response["DBInstances"]:
            for sg in instance["VpcSecurityGroups"]:
                sgs.add(sg["VpcSecurityGroupId"])

    while "Marker" in response:
        response = session_objects["rds_client"].describe_db_instances(
            MaxRecords=100, Marker=response["Marker"]
        )
        for instance in response["DBInstances"]:
            for sg in instance["VpcSecurityGroups"]:
                sgs.add(sg["VpcSecurityGroupId"])

    return sgs


def list_elb_attached_sgs(session, region):
    """Return security groups attached to ELBs"""

    session_objects = set_session_objects(session, clients=["elb"], region=region)
    sgs = set()

    logger.info("Service: ELB")
    response = session_objects["elb_client"].describe_load_balancers(PageSize=400)

    if response:
        for lb in response["LoadBalancerDescriptions"]:
            for sg in lb.get("SecurityGroups", []):
                sgs.add(sg)

    while "NextMarker" in response:
        response = session_objects["elb_client"].describe_load_balancers(
            PageSize=400, Marker=response["NextMarker"]
        )
        for lb in response["LoadBalancerDescriptions"]:
            for sg in lb.get("SecurityGroups", []):
                sgs.add(sg)

    return sgs


def list_elbv2_attached_sgs(session, region):
    """Return security groups attached to ELBv2s"""

    session_objects = set_session_objects(session, clients=["elbv2"], region=region)
    sgs = set()

    logger.info("Service: ELBv2")
    response = session_objects["elbv2_client"].describe_load_balancers(PageSize=400)

    if response:
        for lb in response["LoadBalancers"]:
            for sg in lb.get("SecurityGroups", []):
                sgs.add(sg)

    while "NextMarker" in response:
        response = session_objects["elbv2_client"].describe_load_balancers(
            PageSize=400, Marker=response["NextMarker"]
        )
        for lb in response["LoadBalancers"]:
            for sg in lb.get("SecurityGroups", []):
                sgs.add(sg)

    return sgs


def list_lambda_attached_sgs(session, region):
    """Return security groups attached to Lambdas"""

    session_objects = set_session_objects(session, clients=["lambda"], region=region)
    sgs = set()

    logger.info("Service: Lambda")
    response = session_objects["lambda_client"].list_functions(MaxItems=50)

    if response:
        for function in response["Functions"]:
            for sg in function.get("VpcConfig", {}).get("SecurityGroupIds", []):
                sgs.add(sg)

    while "NextMarker" in response:
        response = session_objects["lambda_client"].list_functions(
            MaxItems=50, Marker=response["NextMarker"]
        )
        for function in response["Functions"]:
            for sg in function.get("VpcConfig", {}).get("SecurityGroupIds", []):
                sgs.add(sg)

    return sgs


def list_redshift_attached_sgs(session, region):
    """Return security groups attached to Redshift clusters"""

    session_objects = set_session_objects(session, clients=["redshift"], region=region)
    sgs = set()

    logger.info("Service: Redshift")
    response = session_objects["redshift_client"].describe_clusters(MaxRecords=100)

    if response:
        for cluster in response["Clusters"]:
            sg_response = cluster.get("VpcSecurityGroups")
            if sg_response:
                for sg in sg_response:
                    sgs.add(sg["VpcSecurityGroupId"])

    while "Marker" in response:
        response = session_objects["redshift_client"].describe_clusters(
            MaxRecords=100, Marker=response["Marker"]
        )
        for cluster in response["Clusters"]:
            sg_response = cluster.get("VpcSecurityGroups")
            if sg_response:
                for sg in sg_response:
                    sgs.add(sg["VpcSecurityGroupId"])

    return sgs


def list_elasticache_attached_sgs(session, region):
    """Return security groups attached to ElastiCache clusters"""

    session_objects = set_session_objects(
        session, clients=["elasticache"], region=region
    )
    sgs = set()

    logger.info("Service: ElastiCache")
    response = session_objects["elasticache_client"].describe_cache_clusters(
        MaxRecords=100
    )

    if response:
        for cluster in response["CacheClusters"]:
            sg_ids = cluster.get("SecurityGroups")
            if sg_ids:
                sgs.update(sg_ids)

    while "Marker" in response:
        response = session_objects["elasticache_client"].describe_cache_clusters(
            MaxRecords=100, Marker=response["Marker"]
        )
        for cluster in response["CacheClusters"]:
            sg_ids = cluster.get("SecurityGroups")
            if sg_ids:
                sgs.update(sg_ids)

    return sgs


def list_emr_attached_sgs(session, region):
    """Return security groups attached to EMR clusters"""

    session_objects = set_session_objects(session, clients=["emr"], region=region)
    sgs = set()

    logger.info("Service: EMR")
    response = session_objects["emr_client"].list_clusters(
        ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"]
    )

    if response:
        for cluster in response["Clusters"]:
            cluster_id = cluster["Id"]
            cluster_response = session_objects["emr_client"].describe_cluster(
                ClusterId=cluster_id
            )

            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "EmrManagedMasterSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "EmrManagedSlaveSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "ServiceAccessSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "AdditionalMasterSecurityGroups"
            )
            if sg_ids:
                sgs.update(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "AdditionalSlaveSecurityGroups"
            )
            if sg_ids:
                sgs.update(sg_ids)

    while "Marker" in response:
        response = session_objects["emr_client"].list_clusters(
            ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"],
            Marker=response["Marker"],
        )
        for cluster in response["Clusters"]:
            cluster_id = cluster["Id"]
            cluster_response = session_objects["emr_client"].describe_cluster(
                ClusterId=cluster_id
            )

            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "EmrManagedMasterSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "EmrManagedSlaveSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "ServiceAccessSecurityGroup"
            )
            if sg_ids:
                sgs.add(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "AdditionalMasterSecurityGroups"
            )
            if sg_ids:
                sgs.update(sg_ids)
            sg_ids = cluster_response["Cluster"]["Ec2InstanceAttributes"].get(
                "AdditionalSlaveSecurityGroups"
            )
            if sg_ids:
                sgs.update(sg_ids)

    return sgs


def list_ecs_attached_sgs(session, region):
    """Return security groups attached to ECS tasks"""

    session_objects = set_session_objects(session, clients=["ecs"], region=region)
    sgs = set()

    logger.info("Service: ECS")

    # Paginate through ECS clusters
    def list_clusters():
        next_token = None
        while True:
            request_args = {"maxResults": 100}
            if next_token:
                request_args["nextToken"] = next_token
            response = session_objects["ecs_client"].list_clusters(**request_args)
            for cluster_arn in response["clusterArns"]:
                yield cluster_arn
            next_token = response.get("nextToken")
            if not next_token:
                break

    # Paginate through ECS tasks to collect SGs
    def list_tasks_and_collect_sgs(cluster_arn):
        next_token = None
        while True:
            request_args = {"cluster": cluster_arn, "maxResults": 100}
            if next_token:
                request_args["nextToken"] = next_token

            tasks_response = session_objects["ecs_client"].list_tasks(**request_args)

            task_arns = tasks_response.get("taskArns", [])
            if task_arns:
                described_tasks_response = session_objects["ecs_client"].describe_tasks(
                    cluster=cluster_arn, tasks=task_arns
                )
                described_tasks = described_tasks_response.get("tasks", [])
                for task in described_tasks:
                    for attachment in task.get("attachments", []):
                        for detail in attachment.get("details", []):
                            if detail.get("name") == "securityGroup":
                                sgs.add(detail["value"])

            next_token = tasks_response.get("nextToken")
            if not next_token:
                break

    for arn in list_clusters():
        list_tasks_and_collect_sgs(arn)

    return sgs


def list_neptune_attached_sgs(session, region):
    """Return security groups attached to Neptune instances"""

    session_objects = set_session_objects(session, clients=["neptune"], region=region)
    sgs = set()

    logger.info("Service: Neptune")
    response = session_objects["neptune_client"].describe_db_instances(MaxRecords=100)

    if response:
        for instance in response["DBInstances"]:
            for sg in instance["VpcSecurityGroups"]:
                sgs.add(sg["VpcSecurityGroupId"])

    while "Marker" in response:
        response = session_objects["neptune_client"].describe_db_instances(
            MaxRecords=100, Marker=response["Marker"]
        )
        for instance in response["DBClusters"]:
            for sg in instance["VpcSecurityGroups"]:
                sgs.add(sg["VpcSecurityGroupId"])

    return sgs


def list_opensearch_attached_sgs(session, region):
    """Return security groups attached to OpenSearch clusters"""

    session_objects = set_session_objects(
        session, clients=["opensearch"], region=region
    )
    sgs = set()

    logger.info("Service: OpenSearch")
    response = session_objects["opensearch_client"].list_domain_names()

    if response:
        for domain in response["DomainNames"]:
            domain_name = domain["DomainName"]
            domain_response = session_objects["opensearch_client"].describe_domain(
                DomainName=domain_name
            )
            sg_ids = domain_response["DomainStatus"]["VPCOptions"]["SecurityGroupIds"]
            sgs.update(sg_ids)

    return sgs


def list_msk_attached_sgs(session, region):
    """Return security groups attached to MSK clusters"""

    session_objects = set_session_objects(session, clients=["kafka"], region=region)
    sgs = set()

    logger.info("Service: MSK")
    response = session_objects["kafka_client"].list_clusters(MaxResults=100)

    if response:
        for cluster in response["ClusterInfoList"]:
            sgs.update(cluster["BrokerNodeGroupInfo"]["SecurityGroups"])

    while "NextToken" in response:
        response = session_objects["kafka_client"].list_clusters(
            MaxResults=100, NextToken=response["NextToken"]
        )
        for cluster in response["ClusterInfoList"]:
            sgs.update(cluster["BrokerNodeGroupInfo"]["SecurityGroups"])

    return sgs
