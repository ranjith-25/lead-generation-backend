import re


def normalize_string(value: str) -> str:
    """
    Normalize a string into snake_case.

    Examples:
        "Project Domain"      -> "project_domain"
        "Project-Domain"      -> "project_domain"
        "projectDomain"       -> "project_domain"
        "PROJECT DOMAIN"      -> "project_domain"
        "  Project  Domain "  -> "project_domain"
    """
    if not value:
        return ""

    # Convert camelCase/PascalCase to snake_case
    value = re.sub(r'(?<!^)(?=[A-Z])', '_', value)

    # Replace spaces and hyphens with underscores
    value = re.sub(r'[\s\-]+', '_', value)

    # Remove special characters except underscores
    value = re.sub(r'[^a-zA-Z0-9_]', '', value)

    # Collapse multiple underscores
    value = re.sub(r'_+', '_', value)

    return value.strip("_").lower()