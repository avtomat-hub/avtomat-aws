import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {"strict": False, "region": None, "debug": False, "silent": False}
RULES = []


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_permissive_policies(**kwargs):
    """Discover overly permissive IAM policies"""

    session_objects = set_session_objects(
        kwargs["session"], resources=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering permissive policies")

    policies = []
    iterator = session_objects["iam_resource"].policies.filter(
        Scope="Local", OnlyAttached=False, PolicyUsageFilter="PermissionsPolicy"
    )
    for policy in iterator:
        for statement in policy.default_version.document["Statement"]:
            if statement["Effect"] == "Allow":
                if kwargs["strict"]:
                    if is_permissive_resource(statement) or is_permissive_action(
                        statement
                    ):
                        policies.append(policy.policy_name)
                        break  # Only need to find one permissive statement
                else:
                    if is_permissive_resource(statement) and is_permissive_action(
                        statement
                    ):
                        policies.append(policy.policy_name)
                        break  # Only need to find one permissive statement

    logger.info(f"{len(policies)} policies found")
    logger.debug(policies)

    return policies


def is_permissive_policy(policy, strict=False):
    """Check if a policy document is overly permissive"""
    for statement in policy["Statement"]:
        if statement["Effect"] == "Allow":
            if strict:
                if is_permissive_resource(statement) or is_permissive_action(statement):
                    return True
            else:
                if is_permissive_resource(statement) and is_permissive_action(
                    statement
                ):
                    return True
    return False


def is_permissive_resource(statement):
    """Check if  resource is overly permissive"""
    resource = statement["Resource"]
    if isinstance(resource, str):
        return resource == "*"
    elif isinstance(resource, list):
        return "*" in resource
    else:
        raise TypeError(
            f"Unknown type for 'Resource' in policy: {type(resource)}. Expected str or list."
        )


def is_permissive_action(statement):
    """Check if an action is overly permissive"""
    action = statement["Action"]
    if isinstance(action, str):
        return "*" in action
    elif isinstance(action, list):
        return any("*" in act for act in action)
    else:
        raise TypeError(
            f"Unknown type for 'Action' in policy: {type(action)}. Expected str or list."
        )
