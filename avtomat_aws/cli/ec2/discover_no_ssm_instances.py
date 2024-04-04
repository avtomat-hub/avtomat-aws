from avtomat_aws.services.ec2 import discover_no_ssm_instances

ACTION_DESCRIPTION = "Discover EC2 instances without SSM enabled."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--instance_ids",
        nargs="+",
        help="Instance IDs to focus on, separated by space.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = discover_no_ssm_instances(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
