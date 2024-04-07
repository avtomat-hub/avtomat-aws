from .table import output_table


def set_output(data, inputs):
    """Print the result of an action."""

    if inputs.get("output") == "table":
        output_table(data)
    else:
        print(data)
