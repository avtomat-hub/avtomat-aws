from avtomat_aws.services.iam import modify_access_keys

ACTION_DESCRIPTION = "Enable or disable an IAM access key."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--key",
        help="Access key with Id and Username. Repeatable for multiple keys.",
        action="append",
        nargs=2,
        metavar=("ID", "USER"),
        required=True,
    )
    parser.add_argument(
        "--enable", action="store_true", help="Enable the access key.", required=False
    )
    parser.add_argument(
        "--disable", action="store_true", help="Disable the access key.", required=False
    )


def cli(args):
    """Command-line interface function"""

    keys = [{"AccessKeyId": key[0], "UserName": key[1]} for key in args.key]

    inputs = {
        "keys": keys,
        "enable": args.enable,
        "disable": args.disable,
        "region": args.region,
        "debug": args.debug,
        "silent": args.silent,
    }

    try:
        result = modify_access_keys(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
