from avtomat_aws.helpers.set_defaults import set_defaults
from avtomat_aws.validations.validate import validate as perform_validation


def validate(defaults=None, param_rules=None):
    """Decorator to apply default values and validate input parameters for the action."""

    defaults = defaults or {}
    param_rules = param_rules or []

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Set defaults,supplied kwargs take precedence
            kwargs = set_defaults(kwargs, defaults)
            # Validate input parameters
            perform_validation(kwargs, param_rules)
            # Call the action
            return func(*args, **kwargs)

        return wrapper

    return decorator
