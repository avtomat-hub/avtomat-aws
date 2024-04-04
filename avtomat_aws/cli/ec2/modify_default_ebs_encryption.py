from avtomat_aws.services.ec2 import modify_default_ebs_encryption

ACTION_DESCRIPTION = "Modify default EBS encryption."


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable default EBS encryption.",
        required=False,
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable default EBS encryption.",
        required=False,
    )
    parser.add_argument(
        "--change_kms_key",
        action="store_true",
        help="Change the KMS Key used for encryption.",
        required=False,
    )
    parser.add_argument(
        "--kms_key_id", help="KMS Key ID to use for encryption.", required=False
    )
    parser.add_argument(
        "--reset_kms_key",
        action="store_true",
        help="Reset the KMS Key used for encryption to AWS EBS default.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        modify_default_ebs_encryption(**inputs)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
