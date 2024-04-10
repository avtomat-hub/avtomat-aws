from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.ec2 import delete_instances

ACTION_DESCRIPTION = (
    "Delete EC2 instances and, optionally, any associated resource types."
)


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--instance_ids",
        nargs="+",
        help="Instance IDs to delete, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--include",
        nargs="+",
        help="Associated resource types to delete, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--final_image",
        action="store_true",
        help="Create an image (AMI) before deletion.",
        required=False,
    )
    parser.add_argument(
        "--disable_protections",
        action="store_true",
        help="Disable termination and stop protection before deletion.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_instances(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
