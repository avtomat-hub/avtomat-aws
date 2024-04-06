from .config import config


def validate(kwargs, param_rules):
    """Validate input parameters."""

    # Evaluate dynamic rules
    for rule in param_rules:
        for rule_type, params in rule.items():
            rule_func = config.get(rule_type)
            if rule_func:
                rule_func(kwargs, params)
            else:
                raise ValueError(f"Invalid rule type '{rule_type}'")

    # Evaluate logging rule
    rule_func = config.get("logging")
    rule_func(kwargs)
