"""
Input validation utilities.
"""

import re
from typing import Dict, List, Any, Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, ""


def validate_required_field(value: Any, field_name: str) -> Tuple[bool, str]:
    """
    Validate that a required field has a value.

    Args:
        value: Field value
        field_name: Name of the field

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"

    return True, ""


def validate_text_length(text: str, field_name: str,
                        min_length: int = 0,
                        max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate text length constraints.

    Args:
        text: Text to validate
        field_name: Name of the field
        min_length: Minimum required length
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        text = ""

    length = len(text.strip())

    if length < min_length:
        return False, f"{field_name} must be at least {min_length} characters"

    if length > max_length:
        return False, f"{field_name} must not exceed {max_length} characters"

    return True, ""


def validate_form_submission(fields: Dict[str, Any],
                            field_config: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate a complete form submission.

    Args:
        fields: Dictionary of field values
        field_config: List of field configuration dictionaries

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    for config in field_config:
        field_name = config['name']
        field_label = config['label']
        is_required = config.get('required', False)
        field_type = config.get('type', 'text')

        value = fields.get(field_name)

        # Check required fields
        if is_required:
            is_valid, error = validate_required_field(value, field_label)
            if not is_valid:
                errors.append(error)
                continue

        # Skip validation for empty optional fields
        if not value and not is_required:
            continue

        # Validate text fields
        if field_type in ['text', 'textarea']:
            if field_type == 'text':
                is_valid, error = validate_text_length(value, field_label, 0, 200)
            else:  # textarea
                is_valid, error = validate_text_length(value, field_label, 0, 5000)

            if not is_valid:
                errors.append(error)

        # Validate select fields
        elif field_type == 'select':
            options = config.get('options', [])
            if value not in options:
                errors.append(f"{field_label} must be one of the available options")

        # Validate multiselect fields
        elif field_type == 'multiselect':
            if not isinstance(value, list):
                errors.append(f"{field_label} must be a list")

    return len(errors) == 0, errors


def sanitize_html_content(content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    Removes potentially dangerous HTML tags and attributes.

    Args:
        content: HTML content to sanitize

    Returns:
        Sanitized content
    """
    # Remove script tags
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove javascript: protocols
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)

    # Remove on* event handlers
    content = re.sub(r'\son\w+\s*=', '', content, flags=re.IGNORECASE)

    return content


def validate_project_name(project_name: str, available_projects: List[str] = None) -> Tuple[bool, str]:
    """
    Validate project name.

    Args:
        project_name: Project name to validate
        available_projects: List of valid project names (None for manual entry only)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not project_name or not project_name.strip():
        return False, "Project name is required"

    # If no project list (manual entry mode), just validate length
    if available_projects is None:
        is_valid, error = validate_text_length(project_name, "Project name", 1, 100)
        return is_valid, error

    # Allow "Other" or custom project names
    if project_name == "Other" or project_name not in available_projects:
        # Validate custom project name
        is_valid, error = validate_text_length(project_name, "Project name", 1, 100)
        return is_valid, error

    return True, ""
