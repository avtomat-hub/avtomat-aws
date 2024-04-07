from avtomat_aws.services.ec2 import create_snapshots

ACTION_DESCRIPTION = "Create EBS snapshots from volumes."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--volume_ids",
        nargs="+",
        help="Volume IDs to create snapshots for, separated by space.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = create_snapshots(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
