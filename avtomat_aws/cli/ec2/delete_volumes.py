from avtomat_aws.services.ec2 import delete_volumes
from avtomat_aws.helpers.cli.set_output import set_output

ACTION_DESCRIPTION = "Delete EBS volumes."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--volume_ids",
        nargs="+",
        help="Volume IDs to delete, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Create snapshots before deletion.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_volumes(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
