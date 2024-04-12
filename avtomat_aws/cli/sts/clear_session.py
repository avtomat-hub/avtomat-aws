import os

ACTION_DESCRIPTION = "Clear an authenticated session."


def clear_environment_bash():
    """Clear environment variables in Bash"""
    commands = f"""
            unset AWS_ACCESS_KEY_ID;
            unset AWS_SECRET_ACCESS_KEY;
            unset AWS_SESSION_TOKEN;
            """
    print(commands)


def clear_environment_powershell():
    """Clear environment variables in PowerShell"""
    commands = (
        f"$Env:AWS_ACCESS_KEY_ID=''; "
        f"$Env:AWS_SECRET_ACCESS_KEY=''; "
        f"$Env:AWS_SESSION_TOKEN='';"
    )
    print(commands)


def add_cli_arguments(parser):
    """Argument parsing"""
    pass


def cli(args):
    """Command-line interface function"""

    try:
        if os.name == "nt":
            clear_environment_powershell()
        else:
            clear_environment_bash()
    except Exception as e:
        print(f"Action failed - {e}")
        exit(1)
