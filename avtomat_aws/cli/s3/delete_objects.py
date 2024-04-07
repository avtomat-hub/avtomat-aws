from avtomat_aws.services.s3 import delete_objects

ACTION_DESCRIPTION = "Delete objects from an S3 bucket."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--bucket", help="Name of the S3 bucket to delete objects from.", required=True
    )
    required.add_argument(
        "--objects",
        nargs="+",
        help="Objects to delete, separated by space.",
        required=True,
    )
    parser.add_argument("--prefix", help="Prefix to filter objects by.", required=False)


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_objects(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
