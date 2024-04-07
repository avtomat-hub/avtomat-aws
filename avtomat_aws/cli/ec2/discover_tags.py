from avtomat_aws.services.ec2 import discover_tags

ACTION_DESCRIPTION = "Find existing or missing tags on EC2 resources."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--resource_types",
        nargs="+",
        help="List of EC2 resource types to search through.",
        required=True,
    )
    required.add_argument(
        "--tags",
        nargs="+",
        help="Tags in 'Key=Value' or 'Key' format to search for.",
        required=True,
    )
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Search for resources that have the tags.",
        required=False,
    )
    parser.add_argument(
        "--missing",
        action="store_true",
        help="Search for resources that don't have the tags.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_tags(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
