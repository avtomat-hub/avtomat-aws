from avtomat_aws.services.ec2 import share_snapshots
from avtomat_aws.helpers.cli.set_output import set_output

ACTION_DESCRIPTION = "Share EC2 snapshots with other accounts."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--snapshot_ids",
        nargs="+",
        help="EC2 snapshot IDs to move, separated by space.",
        required=True,
    )
    required.add_argument(
        "--target_account", help="Target account for the snapshots.", required=True
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = share_snapshots(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
