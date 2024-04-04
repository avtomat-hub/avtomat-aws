from avtomat_aws.helpers.set_region import set_region
from avtomat_aws.helpers.set_session import set_session


def authenticate():
    """Decorator to authenticate with AWS and set a region for the action."""

    def decorator(func):
        def wrapper(**kwargs):
            # Check if session is not provided and create one if necessary
            if not kwargs.get("session"):
                kwargs["session"] = set_session(
                    debug=kwargs.get("debug"), silent=kwargs.get("silent")
                )
            # Set the region for the session
            kwargs["region"] = set_region(
                region=kwargs.get("region"),
                session=kwargs.get("session"),
                debug=kwargs.get("debug"),
                silent=kwargs.get("silent"),
            )
            # Now that 'session' and 'region' are ensured, call the action
            return func(**kwargs)

        return wrapper

    return decorator
