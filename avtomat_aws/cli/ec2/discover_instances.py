from avtomat_aws.services.ec2 import discover_instances

ACTION_DESCRIPTION = "Discover instances."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--states",
        nargs="+",
        help="Instance states, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        help="Tags for discovery in Key=Value format, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--instance_ids",
        nargs="+",
        help="Instance IDs to focus on, separated by space.",
        required=False,
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="If instance_ids is supplied, return the ones that didn't conform to the filters.",
        required=False,
    )
    parser.add_argument(
        "--os", help="Return only Windows or Linux instances.", required=False
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Get only public instances.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_instances(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
