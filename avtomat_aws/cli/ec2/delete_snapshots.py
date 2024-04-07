from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.ec2 import delete_snapshots

ACTION_DESCRIPTION = "Delete EBS snapshots."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--snapshot_ids",
        nargs="+",
        help="Snapshot IDs to delete, separated by space.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_snapshots(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
