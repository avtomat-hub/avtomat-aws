from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.iam import discover_no_mfa_users

ACTION_DESCRIPTION = "Discover IAM users without MFA enabled."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_no_mfa_users(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
