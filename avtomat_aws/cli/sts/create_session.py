from avtomat_aws.services.sts import create_session

ACTION_DESCRIPTION = "Create an authenticated session."


def print_export_commands(session):
    """Print credentials for CLI"""

    credentials = session.get_credentials()
    current_credentials = credentials.get_frozen_credentials()

    print(f"export AWS_ACCESS_KEY_ID={current_credentials.access_key}")
    print(f"export AWS_SECRET_ACCESS_KEY={current_credentials.secret_key}")
    print(f"export AWS_SESSION_TOKEN={current_credentials.token}")


def add_cli_arguments(parser):
    """Argument parsing"""

    parser.add_argument("--access_key", help="AWS Access Key", required=False)
    parser.add_argument("--secret_key", help="AWS Secret Key", required=False)
    parser.add_argument("--session_token", help="AWS Session Token", required=False)
    parser.add_argument("--profile", help="AWS Profile", required=False)
    parser.add_argument("--role_arn", help="Role ARN to assume", required=False)
    parser.add_argument("--mfa_serial", help="MFA Serial Number", required=False)
    parser.add_argument("--mfa_token", help="MFA Token", required=False)


def cli(args):
    """Command-line interface function"""

    inputs = vars(args)

    try:
        result = create_session(**inputs)
        print_export_commands(result)
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
