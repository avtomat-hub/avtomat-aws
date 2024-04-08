def format_tags(tags, creation=False):
    """Format tags into a list of dictionaries"""
    formatted_tags = []
    # Format tags for creation
    # AWS doesn't accept None and requires at least an empty string for Value
    if creation:
        for tag in tags:
            if "=" in tag:
                key, value = tag.split("=", 1)
                formatted_tags.append({"Key": key, "Value": value})
            else:
                key = tag
                formatted_tags.append({"Key": key, "Value": ""})
    # Format tags for discovery or deletion
    else:
        for tag in tags:
            if "=" in tag:
                key, value = tag.split("=", 1)
                formatted_tags.append({"Key": key, "Value": value})
            else:
                key = tag
                formatted_tags.append({"Key": key})
    return formatted_tags
