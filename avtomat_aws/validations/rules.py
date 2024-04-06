from datetime import datetime, timedelta, timezone


def required_rule(kwargs, params):
    """Validates that required parameters are provided."""

    for param in params:
        if param not in kwargs or kwargs[param] is None:
            raise ValueError(f"Required parameter '{param}' not specified")


def choice_rule(kwargs, params):
    """Validates that parameter values are within allowed choices."""

    for param_dict in params:
        for param, choices in param_dict.items():
            if kwargs[param] is not None and type(kwargs[param]) is list:
                for value in kwargs[param]:
                    if value not in choices:
                        raise ValueError(
                            f"Invalid value for '{param}' - '{value}'. Valid values: {choices}"
                        )
            else:
                if kwargs[param] is not None and kwargs[param] not in choices:
                    raise ValueError(
                        f"Invalid value for '{param}' - '{kwargs[param]}'. Valid values: {choices}"
                    )


def and_rule(kwargs, params):
    """Validates that if either 'x' or 'y' is provided, then both must be provided."""

    try:
        x, y = params
    except ValueError:
        raise ValueError("Rule 'and' requires two parameters")

    if (kwargs.get(x) and not kwargs.get(y)) or (not kwargs.get(x) and kwargs.get(y)):
        raise ValueError(f"'{x}' and '{y}' must be used together")


def at_most_one_rule(kwargs, params):
    """Validates that at most one of the parameters is provided."""

    if len(params) < 2:
        raise ValueError("Rule 'at_most_one' requires at least two parameters")

    params_defined = sum(kwargs.get(param) not in (None, []) for param in params)
    if params_defined > 1:
        raise ValueError(
            f"The following parameters cannot be used together, select only one: {params}"
        )


def at_least_one_rule(kwargs, params):
    """Validates that at least one of the parameters is provided."""

    for param in params:
        if kwargs.get(param):
            return
    raise ValueError(f"At least one of the following parameters is required: {params}")


def logging_rule(kwargs):
    """Validates that 'debug' and 'silent' log levels are not both set."""

    if kwargs.get("debug") and kwargs.get("silent"):
        raise ValueError("Cannot set both 'debug' and 'silent' log levels")


def date_yymmdd_rule(kwargs, params):
    """Validates that date parameters are in the correct format (YYYY/MM/DD)."""

    for param in params:
        if kwargs.get(param):
            try:
                kwargs[param] = datetime.strptime(kwargs[param], "%Y/%m/%d")
            except ValueError:
                raise ValueError(
                    f"'{param}' '{kwargs[param]}' does not match the format YYYY/MM/DD"
                )


def cloudtrail_rule(kwargs, params):
    """Validates that a date is not in the future or not more than 90 days in the past."""

    for param in params:
        if kwargs.get(param):
            if kwargs[param] < datetime.now(timezone.utc) - timedelta(days=90):
                raise ValueError(
                    f"'{param}' '{kwargs[param]}' cannot be more than 90 days in the past"
                )
            if kwargs[param] > datetime.now(timezone.utc):
                raise ValueError(f"'{param}' '{kwargs[param]}' cannot be in the future")
