from avtomat_aws.services.ec2 import discover_volumes

ACTION_DESCRIPTION = "Discover EBS volumes."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--instance_ids",
        nargs="+",
        help="Get volumes attached to specified instances.",
        required=False,
    )
    parser.add_argument(
        "--volume_ids",
        nargs="+",
        help="Volume IDs to focus on, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--unencrypted",
        action="store_true",
        help="Get only unencrypted volumes.",
        required=False,
    )
    parser.add_argument(
        "--detached",
        action="store_true",
        help="Get only detached volumes.",
        required=False,
    )
    parser.add_argument(
        "--types",
        nargs="+",
        help="Volume types to check, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--root",
        action="store_true",
        help="Get only root volumes.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_volumes(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
