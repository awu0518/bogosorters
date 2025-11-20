"""
Simple validation utilities for API input validation.
"""


class ValidationError(ValueError):
    """Custom exception for validation errors."""
    pass


def validate_required_fields(data: dict, required_fields: list) -> None:
    """
    Check if all required fields are present and not empty.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Raises:
        ValidationError: If any required field is missing or empty
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")

    missing = []
    empty = []

    for field in required_fields:
        if field not in data:
            missing.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty.append(field)

    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
    if empty:
        raise ValidationError(f"Fields cannot be empty: {', '.join(empty)}")


def validate_string_length(value: str, field_name: str, max_length: int = 100) -> None:
    """
    Validate string length.

    Args:
        value: String to validate
        field_name: Name of the field
        max_length: Maximum allowed length

    Raises:
        ValidationError: If string is too long
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} must be at most {max_length} characters")
