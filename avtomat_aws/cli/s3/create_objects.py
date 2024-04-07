from avtomat_aws.services.s3 import create_objects

ACTION_DESCRIPTION = "Create objects in an S3 bucket."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--bucket", help="Name of the S3 bucket to create objects in.", required=True
    )
    required.add_argument(
        "--object",
        help="Object with Key and Body. Repeatable for multiple objects.",
        action="append",
        nargs=2,
        metavar=("KEY", "BODY"),
        required=True,
    )
    parser.add_argument(
        "--prefix", help="Prefix for path to create objects under.", required=False
    )


def cli(args):
    """Command-line interface function"""

    objects = [{"Key": obj[0], "Body": obj[1]} for obj in args.object]

    inputs = {
        "bucket": args.bucket,
        "objects": objects,
        "prefix": args.prefix,
        "region": args.region,
        "debug": args.debug,
        "silent": args.silent,
    }

    try:
        result = create_objects(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
