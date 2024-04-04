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
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
