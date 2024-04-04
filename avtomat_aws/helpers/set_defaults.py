def set_defaults(kwargs, default_values):
    """Set default values for input parameters."""

    if default_values is None:
        return kwargs
    for key, default in default_values.items():
        kwargs[key] = default if kwargs.get(key) is None else kwargs[key]

    return kwargs
