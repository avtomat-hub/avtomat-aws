from avtomat_aws.services.ec2 import discover_unused_security_groups

ACTION_DESCRIPTION = "Discover unused security groups."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_unused_security_groups(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
