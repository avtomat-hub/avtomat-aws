import argparse
import sys
from importlib import import_module, metadata

from .services import SERVICES

VERSION = metadata.version("avtomat_aws")


def display_help():
    """Displays help for the main CLI."""
    print("usage: aaws <service> <action> [parameters]\n")
    print("Avtomat AWS CLI\n")
    print("options:")
    print("    -h, --help            Show this help message and exit.")
    print("    -v, --version         Show the current version and exit.\n")
    print("services:")
    # Display services in two columns
    services_list = list(SERVICES.keys())
    max_length = (
        max(len(service) for service in services_list) + 2
    )  # Dynamically calculate space between columns
    if len(services_list) % 2 != 0:
        services_list.append("")
    for service1, service2 in zip(services_list[::2], services_list[1::2]):
        print(f"    {service1:<{max_length}} {service2}")


def display_service_help(service):
    """Displays help for a specific service including available actions."""
    print("usage: aaws <service> <action> [parameters]\n")
    print("Avtomat AWS CLI\n")
    print("options:")
    print("    -h, --help            Show this help message and exit.")
    print("    -v, --version         Show the current version and exit.\n")
    print("actions:")
    # Display actions in two columns
    actions_list = SERVICES.get(service, [])
    max_length = (
        max(len(action) for action in actions_list) + 2
    )  # Dynamically calculate space between columns
    if len(actions_list) % 2 != 0:
        actions_list.append("")
    for action1, action2 in zip(actions_list[::2], actions_list[1::2]):
        print(f"    {action1:<{max_length}} {action2}")


def display_action_help(service, action):
    """Displays help for a specific action, including action-specific arguments."""
    # Load the module for the action so that we can dynamically generate the help message through argparse
    parser = set_parser(service, action)
    # Print the help message
    parser.print_help()


def load_module(service, action):
    """Dynamically load the module for the given service and action."""
    try:
        module_name = f"avtomat_aws.cli.{service}.{action}"
        return import_module(module_name)
    except ImportError:
        sys.stderr.write(f"Error: Unable to load module for {service} {action}\n")
        sys.exit(1)


def set_parser(service, action):
    """Dynamically set the parser for the given service and action."""

    module = load_module(service, action)
    action_description = getattr(
        module, "ACTION_DESCRIPTION", "No description available"
    )
    parser = argparse.ArgumentParser(
        prog=f"aaws {service} {action}", add_help=False, description=action_description
    )

    # Global arguments
    parser.add_argument(
        "--region",
        help="Region for operation. Leave blank for session default.",
        required=False,
    )
    parser.add_argument(
        "--debug", action="store_true", help="Increase log verbosity.", required=False
    )
    parser.add_argument(
        "--silent", action="store_true", help="Decrease log verbosity.", required=False
    )

    # Use the imported module's function to add its arguments to the parser
    if hasattr(module, "add_cli_arguments"):
        module.add_cli_arguments(parser)
        parser.set_defaults(func=module.cli)
    else:
        print("No arguments defined for this action.")
        return

    return parser


def main():
    """Main function for the CLI."""

    # Version
    if len(sys.argv) == 2 and (sys.argv[1] == "--version" or sys.argv[1] == "-v"):
        print(f"aaws {VERSION}")
        sys.exit(0)

    # Not enough arguments
    if len(sys.argv) < 3:
        display_help()
        sys.exit(1)

    # Invalid service
    if sys.argv[1] not in SERVICES:
        sys.stderr.write(f"Error: Invalid service: {sys.argv[1]}\n")
        sys.exit(1)

    # Only a service with --help or -h
    if len(sys.argv) == 3 and (sys.argv[2] == "--help" or sys.argv[2] == "-h"):
        service = sys.argv[1]
        display_service_help(service)
        sys.exit(0)

    # Invalid action
    if sys.argv[2] not in SERVICES[sys.argv[1]]:
        sys.stderr.write(f"Error: Invalid action: {sys.argv[2]}\n")
        sys.exit(1)

    # A service, action, and --help or -h
    if len(sys.argv) == 4 and (sys.argv[3] == "--help" or sys.argv[3] == "-h"):
        service, action = sys.argv[1:3]
        display_action_help(service, action)
        sys.exit(0)

    # Execute
    service, action = sys.argv[1:3]
    parser = set_parser(service, action)
    args = parser.parse_args(sys.argv[3:])
    args.func(args)


if __name__ == "__main__":
    main()
