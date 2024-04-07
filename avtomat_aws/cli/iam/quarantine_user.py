from avtomat_aws.services.iam import quarantine_user

ACTION_DESCRIPTION = "Disable console and programmatic access and apply AWSCompromisedKeyQuarantineV2 policy to an IAM user."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument("--user", help="User to quarantine.", required=True)


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        quarantine_user(**inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
