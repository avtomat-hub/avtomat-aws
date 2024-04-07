from avtomat_aws.services.ec2 import modify_volumes

ACTION_DESCRIPTION = "Modify EBS volumes."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--volume_ids",
        nargs="+",
        help="Volume IDs to modify, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--size", type=int, help="New size (GB) for volumes.", required=False
    )
    parser.add_argument("--type", help="New type for volumes.", required=False)
    parser.add_argument(
        "--iops", type=int, help="New iops for volumes.", required=False
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Create snapshots before modification.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = modify_volumes(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
