from avtomat_aws.services.general import get_date

ACTION_DESCRIPTION = "Return a date in the requested format."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--after",
        type=int,
        help="Return a date number of days in the future.",
        required=False,
    )
    parser.add_argument(
        "--before",
        type=int,
        help="Return a date number of days in the past.",
        required=False,
    )
    parser.add_argument(
        "--format", help="Return the date in this format.", required=False
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = get_date(**inputs)
        print(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
