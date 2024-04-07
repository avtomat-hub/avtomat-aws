from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.iam import discover_unused_access_keys

ACTION_DESCRIPTION = "Discover IAM access keys not used for over a number of days."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--threshold_days",
        type=int,
        help="Get access keys not used for more than this number of days.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_unused_access_keys(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
