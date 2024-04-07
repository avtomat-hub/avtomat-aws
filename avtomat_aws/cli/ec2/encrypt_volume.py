from avtomat_aws.services.ec2 import encrypt_volume

ACTION_DESCRIPTION = "Encrypt an EBS volume."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument("--volume_id", help="Volume ID to encrypt.", required=True)
    required.add_argument(
        "--kms_key_id", help="KMS Key ID to use for encryption.", required=True
    )
    parser.add_argument(
        "--re_encrypt",
        action="store_true",
        help="Re-encrypt already encrypted volume.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = encrypt_volume(**inputs)
        print(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
