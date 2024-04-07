from avtomat_aws.services.backup import delete_backups

ACTION_DESCRIPTION = "Delete backup recovery points."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--backup_vault_name",
        help="Backup vault from which to delete recovery points.",
        required=True,
    )
    required.add_argument(
        "--recovery_point_arns",
        nargs="+",
        help="Recovery point ARNs to delete, separated by space.",
        required=True,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = delete_backups(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
