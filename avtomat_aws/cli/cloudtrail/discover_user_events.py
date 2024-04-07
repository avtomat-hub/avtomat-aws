from avtomat_aws.services.cloudtrail import discover_user_events

ACTION_DESCRIPTION = "Discover events created by specific user."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--user", help="Search events originating from this user.", required=True
    )
    parser.add_argument(
        "--events",
        nargs="+",
        help="Search for specific events, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--created_after",
        help="Search for events created after this time. (YYYY/MM/DD)",
        required=False,
    )
    parser.add_argument(
        "--created_before",
        help="Search for events created before this time. (YYYY/MM/DD)",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_user_events(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
