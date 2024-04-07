from avtomat_aws.services.ec2 import delete_security_groups

ACTION_DESCRIPTION = "Delete EC2 security groups."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--security_group_ids",
        nargs="+",
        help="Security Group IDs to delete, separated by space.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_security_groups(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
