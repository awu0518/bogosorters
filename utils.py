# Small utility helpers used across the project.

from typing import Any


def normalize_str(value: Any) -> str:
    """Return a trimmed, lowercased string for safe comparisons.

    - Converts non-None, non-string values to string.
    - Returns empty string for ``None``.

    Examples:
        >>> normalize_str('  Foo  ')
        'foo'
        >>> normalize_str(None)
        ''
    """
    if value is None:
        return ''
    if not isinstance(value, str):
        value = str(value)
    return value.strip().lower()
