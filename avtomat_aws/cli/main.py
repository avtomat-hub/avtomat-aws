import argparse
import importlib
import sys

from .services import services


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"aaws: error: {message}\n")


def load_module(collection, action):
    try:
        module_name = f"avtomat_aws.cli.{collection}.{action}"
        return importlib.import_module(module_name)
    except ImportError:
        sys.stderr.write(f"Error: Unable to load module for {collection} {action}\n")
        sys.exit(1)


def set_parser():
    parser = CustomArgumentParser(description="Avtomat AWS CLI")
    subparsers = parser.add_subparsers(dest="collection", required=True)

    for collection, actions in services.items():
        service_parser = subparsers.add_parser(collection)
        service_subparsers = service_parser.add_subparsers(dest="action", required=True)

        for action in actions:
            module = load_module(collection, action)
            cmd_description = getattr(
                module, "ACTION_DESCRIPTION", "No description available"
            )
            cmd_parser = service_subparsers.add_parser(
                action, description=cmd_description
            )

            # Global arguments
            cmd_parser.add_argument(
                "--region",
                help="Region for operation. Leave blank for session default.",
                required=False,
            )
            cmd_parser.add_argument(
                "--debug", action="store_true", help="Increase log verbosity."
            )
            cmd_parser.add_argument(
                "--silent", action="store_true", help="Decrease log verbosity."
            )

            # Action specific arguments
            module.add_cli_arguments(cmd_parser)
            cmd_parser.set_defaults(func=module.cli)

    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
