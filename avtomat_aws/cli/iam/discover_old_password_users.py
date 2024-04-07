from avtomat_aws.services.iam import discover_old_password_users

ACTION_DESCRIPTION = "Discover IAM users with passwords older than a certain age."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--threshold_days",
        type=int,
        help="Get users with a password older than this number of days.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_old_password_users(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
