from avtomat_aws.services.ec2 import copy_snapshots

ACTION_DESCRIPTION = "Move EC2 snapshots between regions or accounts."


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
        "--target_region", help="Target region for the snapshots.", required=True
    )
    parser.add_argument(
        "--pending_limit",
        type=int,
        help="Limit for concurrent snapshot copy operations.",
        required=False,
    )
    parser.add_argument(
        "--encrypt",
        action="store_true",
        help="Encrypt or re-encrypt the snapshots before moving.",
        required=False,
    )
    parser.add_argument(
        "--kms_key_id",
        help="KMS Key ID to use for snapshot encryption.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = copy_snapshots(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
