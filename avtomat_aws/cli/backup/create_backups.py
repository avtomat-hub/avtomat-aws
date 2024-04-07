from avtomat_aws.services.backup import create_backups

ACTION_DESCRIPTION = "Start an on-demand backup job for the specified resources."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--resource_ids",
        nargs="+",
        help="Resource IDs to create backups for, separated by space.",
        required=True,
    )
    required.add_argument(
        "--service", help="Service to which the resource IDs belong.", required=True
    )
    parser.add_argument(
        "--backup_vault_name",
        help="Backup vault in which to store the backups.",
        required=False,
        default="Default",
    )
    parser.add_argument(
        "--retention_days",
        type=int,
        help="Number of days to retain the backups.",
        required=False,
    )
    parser.add_argument(
        "--iam_role",
        help="Role ARN used to create the backup. Leave blank for AWS Backup Default Service Role.",
        required=False,
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for backups to complete before proceeding.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = create_backups(**inputs)
        for item in result:
            print(item)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
