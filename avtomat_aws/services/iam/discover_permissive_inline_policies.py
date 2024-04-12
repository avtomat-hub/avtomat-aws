import logging

from avtomat_aws.decorators.authenticate import authenticate
from avtomat_aws.decorators.set_logger import set_logger
from avtomat_aws.decorators.validate import validate
from avtomat_aws.helpers.set_session_objects import set_session_objects

logger = logging.getLogger(__name__)

DEFAULTS = {
    "focus": ["user", "group", "role"],
    "strict": False,
    "region": None,
    "debug": False,
    "silent": False,
}
RULES = []


@validate(DEFAULTS, RULES)
@set_logger()
@authenticate()
def discover_permissive_inline_policies(**kwargs):
    """Discover overly permissive inline IAM policies"""

    session_objects = set_session_objects(
        kwargs["session"], clients=["iam"], region=kwargs["region"]
    )

    logger.info(f"Discovering permissive inline policies")

    policies = []
    if "user" in kwargs["focus"]:
        paginator = session_objects["iam_client"].get_paginator("list_users")  # Users
        for page in paginator.paginate():
            for user in page["Users"]:
                policies += check_user_inline_policies(
                    session_objects["iam_client"], user, kwargs["strict"]
                )

    if "role" in kwargs["focus"]:
        paginator = session_objects["iam_client"].get_paginator("list_roles")  # Roles
        for page in paginator.paginate():
            for role in page["Roles"]:
                policies += check_role_inline_policies(
                    session_objects["iam_client"], role, kwargs["strict"]
                )

    if "group" in kwargs["focus"]:
        paginator = session_objects["iam_client"].get_paginator("list_groups")  # Groups
        for page in paginator.paginate():
            for group in page["Groups"]:
                policies += check_group_inline_policies(
                    session_objects["iam_client"], group, kwargs["strict"]
                )

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


def check_user_inline_policies(client, user, strict):
    """Retrieve and evaluate inline policies for a user"""
    user_policies = []
    paginator = client.get_paginator("list_user_policies")
    for page in paginator.paginate(UserName=user["UserName"]):
        for policy_name in page["PolicyNames"]:
            policy = client.get_user_policy(
                UserName=user["UserName"], PolicyName=policy_name
            )["PolicyDocument"]
            if is_permissive_policy(policy, strict):
                user_policies.append(
                    {"Type": "User", "Entity": user["UserName"], "Policy": policy_name}
                )
    return user_policies


def check_role_inline_policies(client, role, strict):
    """Retrieve and evaluate inline policies for a role"""
    role_policies = []
    paginator = client.get_paginator("list_role_policies")
    for page in paginator.paginate(RoleName=role["RoleName"]):
        for policy_name in page["PolicyNames"]:
            policy = client.get_role_policy(
                RoleName=role["RoleName"], PolicyName=policy_name
            )["PolicyDocument"]
            if is_permissive_policy(policy, strict):
                role_policies.append(
                    {"Type": "Role", "Entity": role["RoleName"], "Policy": policy_name}
                )
    return role_policies


def check_group_inline_policies(client, group, strict):
    """Retrieve and evaluate inline policies for a group"""
    group_policies = []
    paginator = client.get_paginator("list_group_policies")
    for page in paginator.paginate(GroupName=group["GroupName"]):
        for policy_name in page["PolicyNames"]:
            policy = client.get_group_policy(
                GroupName=group["GroupName"], PolicyName=policy_name
            )["PolicyDocument"]
            if is_permissive_policy(policy, strict):
                group_policies.append(
                    {
                        "Type": "Group",
                        "Entity": group["GroupName"],
                        "Policy": policy_name,
                    }
                )
    return group_policies
