from avtomat_aws.services.iam import discover_unused_roles

ACTION_DESCRIPTION = "Discover IAM roles not used over a certain amount of days."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--threshold_days",
        type=int,
        help="Get roles not used for more than this number of days.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_unused_roles(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
