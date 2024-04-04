from avtomat_aws.services.ec2 import discover_snapshots

ACTION_DESCRIPTION = "Discover snapshots of EBS volumes."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--volume_ids",
        nargs="+",
        help="Get snapshots that originate from specific volumes.",
        required=False,
    )
    parser.add_argument(
        "--snapshot_ids",
        nargs="+",
        help="Snapshot IDs to focus on, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--unencrypted",
        action="store_true",
        help="Get only unencrypted snapshots.",
        required=False,
    )
    parser.add_argument(
        "--exclude_aws_backup",
        action="store_true",
        help="Exclude snapshots managed by AWS Backup.",
        required=False,
    )
    parser.add_argument(
        "--created_before",
        help="Get snapshots created before date (YYYY/MM//DD).",
        required=False,
    )
    parser.add_argument(
        "--created_after",
        help="Get snapshots created after date (YYYY/MM//DD).",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_snapshots(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
