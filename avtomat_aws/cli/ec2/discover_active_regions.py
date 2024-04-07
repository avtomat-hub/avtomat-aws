from avtomat_aws.services.ec2 import discover_active_regions
from avtomat_aws.helpers.cli.set_output import set_output

ACTION_DESCRIPTION = "Discover active regions for an account."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_active_regions(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
