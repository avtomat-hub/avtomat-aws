from avtomat_aws.services.iam import modify_users_console_access

ACTION_DESCRIPTION = "Enable or disable AWS Management Console access for an IAM user."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--user",
        help="User with Username and Password(optional). Repeatable for multiple keys.",
        action="append",
        nargs="+",
        metavar=("USERNAME", "PASSWORD"),
        required=True,
    )
    parser.add_argument(
        "--enable", action="store_true", help="Enable console access.", required=False
    )
    parser.add_argument(
        "--disable", action="store_true", help="Disable console access.", required=False
    )


def cli(args):
    """Command-line interface function"""

    users = [
        {"UserName": u[0], "Password": u[1] if len(u) > 1 else None} for u in args.user
    ]

    inputs = {
        "users": users,
        "enable": args.enable,
        "disable": args.disable,
        "region": args.region,
        "debug": args.debug,
        "silent": args.silent,
    }

    try:
        result = modify_users_console_access(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
