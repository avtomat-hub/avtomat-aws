from avtomat_aws.services.ec2 import discover_images

ACTION_DESCRIPTION = "Discover AWS images (AMI)."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--image_ids",
        nargs="+",
        help="Image IDs to focus on, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Get only publicly exposed images.",
        required=False,
    )
    parser.add_argument(
        "--exclude_aws_backup",
        action="store_true",
        help="Exclude images managed by AWS Backup.",
        required=False,
    )
    parser.add_argument(
        "--created_before",
        help="Get images created before date (YYYY/MM//DD).",
        required=False,
    )
    parser.add_argument(
        "--created_after",
        help="Get images created after date (YYYY/MM//DD).",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_images(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
