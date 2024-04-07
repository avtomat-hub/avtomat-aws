from avtomat_aws.services.ec2 import modify_tags

ACTION_DESCRIPTION = "Modify EC2 resource tags."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--resource_ids",
        nargs="+",
        help="EC2 resource IDs to apply tags to, separated by space.",
        required=True,
    )
    required.add_argument(
        "--tags",
        nargs="+",
        help="Tags to create or delete in Key=Value format, separated by space.",
        required=True,
    )
    parser.add_argument(
        "--create", action="store_true", help="Create tags.", required=False
    )
    parser.add_argument(
        "--delete", action="store_true", help="Delete tags.", required=False
    )
    parser.add_argument(
        "--dynamic_tags",
        action="store_true",
        help="Add resource_id in the tag key or value.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = modify_tags(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
