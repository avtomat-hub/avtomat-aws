import datetime


def preprocess_data(data):
    """Preprocess data for table output."""

    if isinstance(data, dict):
        data = [data]


def table_from_list_dict_data(data):
    """Print a table from a list of dictionaries."""

    headers = sorted(
        set(key for item in data for key in item.keys())
    )  # Sort headers for consistent ordering
    column_widths = {
        header: max(len(header), max(len(str(item.get(header, ""))) for item in data))
        for header in headers
    }

    # Print table header
    header_row = (
        "+" + "+".join(["-" * (column_widths[header] + 2) for header in headers]) + "+"
    )
    print(header_row)
    header_content = "|".join(
        [" " + header.ljust(column_widths[header]) + " " for header in headers]
    )
    print(f"|{header_content}|")
    print(header_row.replace("-", "-"))

    # Print each row of data without dividers between rows
    for item in data:
        row_data = [
            " " + str(item.get(header, "")).ljust(column_widths[header]) + " "
            for header in headers
        ]
        print(f"|{'|'.join(row_data)}|")


def table_from_list_data(data):
    """Print a table from a list of strings."""

    header = "Resources"
    column_width = max(len(header), max(len(item) for item in data))

    # Print table header
    header_row = f"+{'-' * (column_width + 2)}+"
    print(header_row)
    print(f"| {header.center(column_width)} |")
    print(header_row.replace("-", "-"))

    # Print each row without dividers between rows
    for item in data:
        print(f"| {item.center(column_width)} |")


def output_table(data):
    """Print a table for CLI output."""

    if isinstance(data, datetime.datetime):
        table_from_list_data([str(data)])
    elif isinstance(data, dict):
        table_from_list_dict_data([data])
    elif all(isinstance(item, dict) for item in data):
        table_from_list_dict_data(data)
    elif all(isinstance(item, str) for item in data):
        table_from_list_data(data)
    else:
        print("Mixed or unsupported data format.")
