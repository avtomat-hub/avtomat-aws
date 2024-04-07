from avtomat_aws.services.iam import discover_inactive_console_users

ACTION_DESCRIPTION = (
    "Discover IAM users with last console sign-in over a certain period."
)


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--threshold_days",
        type=int,
        help="Get users with last console sign-in over this number of days.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_inactive_console_users(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
