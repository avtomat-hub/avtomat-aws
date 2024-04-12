from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.iam import discover_permissive_inline_policies

ACTION_DESCRIPTION = "Discover IAM inline policies with overly permissive permissions."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Determine mode of evaluation. If set, any permissive Action or Resource is a violation. Otherwise, any permissive Action and Resource is a violation.",
        required=False,
    )
    parser.add_argument(
        "--focus",
        nargs="+",
        help="Resource types to focus on, separated by space.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_permissive_inline_policies(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
