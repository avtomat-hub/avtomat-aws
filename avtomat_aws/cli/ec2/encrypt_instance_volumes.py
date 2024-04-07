from avtomat_aws.services.ec2 import encrypt_instance_volumes

ACTION_DESCRIPTION = "Encrypt all EBS volumes attached to an instance."


def add_cli_arguments(parser):
    """Argument parsing"""

    required = parser.add_argument_group("required")

    required.add_argument(
        "--instance_id", help="Instance ID for volume encryption.", required=True
    )
    required.add_argument(
        "--kms_key_id", help="KMS Key ID to use for encryption.", required=True
    )
    parser.add_argument(
        "--re_encrypt",
        action="store_true",
        help="Re-encrypt already encrypted volumes.",
        required=False,
    )


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = encrypt_instance_volumes(**inputs)
        print(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
