from avtomat_aws.services.ec2 import discover_default_ebs_encryption

ACTION_DESCRIPTION = "Discover default EBS encryption."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_default_ebs_encryption(**inputs)
        print(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
