import logging
import time

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "backup_vault_name": "Default",
    "retention_days": 14,
    "iam_role": None,
    "wait": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = [
    {"required": ["resource_ids", "service"]},
    {"choice": [{"service": ["ec2", "ebs"]}]},
]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def create_backups(**kwargs):
    """Start an on-demand backup job for the specified resources"""

    # Required parameters
    resource_ids = kwargs.pop("resource_ids")
    service = kwargs.pop("service")

    if not resource_ids:
        logger.info("No resources to backup")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["backup", "sts"], region=kwargs["region"]
    )

    current_account = session_objects["sts_client"].get_caller_identity()["Account"]
    if not kwargs.get("iam_role"):
        kwargs["iam_role"] = (
            f"arn:aws:iam::{current_account}:role/service-role/AWSBackupDefaultServiceRole"
        )

    logger.info(f"Creating backups for resources")

    failed_jobs = []
    initiated_jobs = {}
    for resource_id in resource_ids:
        try:
            resource_arn = construct_arn(
                service, resource_id, kwargs["region"], current_account
            )
            response = session_objects["backup_client"].start_backup_job(
                BackupVaultName=kwargs["backup_vault_name"],
                ResourceArn=resource_arn,
                IamRoleArn=kwargs["iam_role"],
                StartWindowMinutes=60,
                Lifecycle={"DeleteAfterDays": kwargs["retention_days"]},
            )
            initiated_jobs[response["BackupJobId"]] = resource_id
        except Exception as e:
            logger.error(f"Failed to create a backup for {resource_id} - {e}")
            failed_jobs.append(resource_id)
            continue

    if kwargs.get("wait"):
        logger.info("Waiting for backup jobs to complete")
        failed_jobs = wait_backups(
            session_objects["backup_client"], initiated_jobs, failed_jobs
        )

    if failed_jobs:
        logger.info(f"{len(failed_jobs)} resources failed backup creation")
    else:
        logger.info("Success")
    logger.debug(failed_jobs)

    return failed_jobs


def wait_backups(backup_client, initiated_jobs, failed_jobs):
    """Wait for backup jobs to complete"""

    while initiated_jobs:
        for job_id, resource_id in list(initiated_jobs.items()):
            try:
                response = backup_client.describe_backup_job(BackupJobId=job_id)
                status = response["State"]
                if status in ["COMPLETED"]:
                    del initiated_jobs[job_id]
                elif status in ["FAILED", "ABORTED"]:
                    del initiated_jobs[job_id]
                    failed_jobs.append(resource_id)
            except Exception as e:
                logger.error(f"Failed to get status for backup of {resource_id} - {e}")
                continue

        if initiated_jobs:
            logger.debug(f"Waiting for {len(initiated_jobs)} backup jobs to complete")
            time.sleep(60)

    return failed_jobs


def construct_arn(service, resource_id, region, account_id):
    """Construct ARN for the specified resource"""

    if service == "ec2":
        return f"arn:aws:ec2:{region}:{account_id}:instance/{resource_id}"
    if service == "ebs":
        return f"arn:aws:ec2:{region}:{account_id}:volume/{resource_id}"
