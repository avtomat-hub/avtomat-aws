import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"region": None, "debug": False, "silent": False}
RULES = [{"required": ["backup_vault_name", "recovery_point_arns"]}]


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def delete_backups(**kwargs):
    """Delete backup recovery points"""

    # Required parameters
    backup_vault_name = kwargs.pop("backup_vault_name")
    recovery_point_arns = kwargs.pop("recovery_point_arns")

    if not recovery_point_arns:
        logger.info("No recovery points to delete")
        return []

    session_objects = set_session_objects(
        kwargs["session"], clients=["backup"], region=kwargs["region"]
    )

    logger.info(f"Deleting recovery points from '{backup_vault_name}' backup vault")

    failed = []
    counter = 0
    for arn in recovery_point_arns:
        try:
            session_objects["backup_client"].delete_recovery_point(
                BackupVaultName=backup_vault_name, RecoveryPointArn=arn
            )
            logger.info(f"{arn} - deleted")
            counter += 1
        except Exception as e:
            failed.append(arn)
            logger.error(f"{arn} - failed to delete - {e}")

    logger.info(f"{counter} recovery points deleted")
    if failed:
        logger.warning(f"{len(failed)} recovery points failed to delete")
        logger.debug(failed)

    return failed
