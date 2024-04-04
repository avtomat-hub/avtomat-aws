from avtomat_aws.services.ec2 import discover_active_regions

ACTION_DESCRIPTION = "Discover active regions for an account."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_active_regions(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
