from avtomat_aws.services.s3 import discover_objects

ACTION_DESCRIPTION = "Discover objects in an S3 bucket."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--bucket", help="Name of the S3 bucket to discover objects in.", required=True
    )
    parser.add_argument("--prefix", help="Prefix to filter objects by.", required=False)
    parser.add_argument(
        "--modified_before",
        help="Get objects last modified before date (YYYY/MM//DD).",
        required=False,
    )
    parser.add_argument(
        "--modified_after",
        help="Get objects last modified after date (YYYY/MM//DD).",
        required=False,
    )
    parser.add_argument(
        "--name_only",
        action="store_true",
        help="Return only the object name, not the entire path.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_objects(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
