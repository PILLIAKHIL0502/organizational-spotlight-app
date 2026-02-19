"""
Utility helper functions.
"""

from datetime import datetime
from typing import Dict, Any, List


def format_date(dt: datetime, format_str: str = '%B %d, %Y') -> str:
    """
    Format a datetime object to a string.

    Args:
        dt: Datetime object
        format_str: Format string (default: Month Day, Year)

    Returns:
        Formatted date string
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = '%B %d, %Y at %I:%M %p') -> str:
    """
    Format a datetime object to a string with time.

    Args:
        dt: Datetime object
        format_str: Format string (default: Month Day, Year at Hour:Minute AM/PM)

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def get_status_badge_color(status: str) -> str:
    """
    Get the appropriate color for a status badge.

    Args:
        status: Status string

    Returns:
        Color name or hex code
    """
    status_colors = {
        'draft': 'gray',
        'submitted': 'blue',
        'under_review': 'orange',
        'approved': 'green',
        'rejected': 'red',
        'published': 'purple',
        'open': 'green'
    }
    return status_colors.get(status.lower(), 'gray')


def get_status_display_name(status: str) -> str:
    """
    Get a human-readable display name for a status.

    Args:
        status: Status string

    Returns:
        Display name
    """
    status_names = {
        'draft': 'Draft',
        'submitted': 'Submitted',
        'under_review': 'Under Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'published': 'Published',
        'open': 'Open'
    }
    return status_names.get(status.lower(), status.title())


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def dict_to_fields(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Convert a dictionary to a list of field dictionaries.

    Args:
        data: Dictionary to convert

    Returns:
        List of field dictionaries
    """
    return [{'name': k, 'value': str(v)} for k, v in data.items()]


def fields_to_dict(fields: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Convert a list of field dictionaries to a dictionary.

    Args:
        fields: List of field dictionaries

    Returns:
        Dictionary
    """
    return {field['name']: field['value'] for field in fields}


def get_current_period() -> tuple:
    """
    Get the current publication period.

    Returns:
        Tuple of (year, month, period)
    """
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    period = 'first_half' if day <= 15 else 'second_half'

    return year, month, period


def format_field_name(field_name: str) -> str:
    """
    Format a field name for display (convert snake_case to Title Case).

    Args:
        field_name: Field name in snake_case

    Returns:
        Formatted field name
    """
    return field_name.replace('_', ' ').title()


def merge_dictionaries(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries, with later dictionaries taking precedence.

    Args:
        *dicts: Variable number of dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_month_name(month: int) -> str:
    """
    Get the full name of a month.

    Args:
        month: Month number (1-12)

    Returns:
        Month name
    """
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    if 1 <= month <= 12:
        return month_names[month - 1]
    return f"Month {month}"


def count_words(text: str) -> int:
    """
    Count the number of words in a text.

    Args:
        text: Text to count words in

    Returns:
        Word count
    """
    if not text:
        return 0
    return len(text.split())
