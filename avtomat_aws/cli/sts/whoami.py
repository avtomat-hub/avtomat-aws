from avtomat_aws.services.sts import whoami

ACTION_DESCRIPTION = "Return current entity."


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = whoami(**inputs)
        print(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
