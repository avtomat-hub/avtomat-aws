from avtomat_aws.services.ec2 import delete_images

ACTION_DESCRIPTION = "Delete EC2 images (AMI)."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--image_ids",
        nargs="+",
        help="Image IDs to delete, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--include_snapshots",
        action="store_true",
        help="Delete snapshots associated with this image.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_images(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
