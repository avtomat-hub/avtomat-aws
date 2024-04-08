from avtomat_aws.helpers.cli.set_output import set_output
from avtomat_aws.services.ec2 import create_images

ACTION_DESCRIPTION = "Create images (AMI) of EC2 instances."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--instance_ids",
        nargs="+",
        help="Instance IDs to create images for, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--reboot",
        action="store_true",
        help="Reboot instances before creating the images.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = create_images(**inputs)
        set_output(result, inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
