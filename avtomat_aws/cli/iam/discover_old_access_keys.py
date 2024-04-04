from avtomat_aws.services.iam import discover_old_access_keys

ACTION_DESCRIPTION = "Discover IAM access keys over a certain age."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required arguments")

    required.add_argument(
        "--threshold_days",
        type=int,
        help="Get access keys older than this number of days.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_old_access_keys(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
