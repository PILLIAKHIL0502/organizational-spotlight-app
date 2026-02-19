"""
Reusable UI components for the Streamlit application.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from jinja2 import Template
from datetime import datetime

from config import settings
from config.branding import BMS_COLORS, STATUS_COLORS, FONTS
from utils.helpers import (
    get_status_badge_color, get_status_display_name,
    format_datetime, truncate_text
)


def render_status_badge(status: str):
    """
    Render a colored status badge with BMS styling.

    Args:
        status: Status string
    """
    display_name = get_status_display_name(status)
    hex_color = STATUS_COLORS.get(status.lower(), '#6c757d')

    st.markdown(
        f'<span class="bms-badge" style="background-color: {hex_color}; color: white; '
        f'font-family: {FONTS["bold"]};">{display_name}</span>',
        unsafe_allow_html=True
    )


def render_submission_form(fields_config: List[Dict[str, Any]],
                          initial_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Render a dynamic submission form based on field configuration.

    Args:
        fields_config: List of field configuration dictionaries
        initial_values: Optional dictionary of initial field values

    Returns:
        Dictionary of field values from the form
    """
    form_data = {}

    if initial_values is None:
        initial_values = {}

    for field in fields_config:
        field_name = field['name']
        field_label = field['label']
        field_type = field['type']
        is_required = field.get('required', False)
        placeholder = field.get('placeholder', '')
        help_text = field.get('help_text', '')

        # Add asterisk for required fields
        label = f"{field_label} {'*' if is_required else ''}"

        # Get initial value
        initial_value = initial_values.get(field_name, '')

        # Render appropriate input widget
        if field_type == 'text':
            value = st.text_input(
                label,
                value=initial_value,
                placeholder=placeholder,
                help=help_text
            )
        elif field_type == 'textarea':
            value = st.text_area(
                label,
                value=initial_value,
                placeholder=placeholder,
                help=help_text,
                height=150
            )
        elif field_type == 'select':
            options = field.get('options', [])
            index = 0
            if initial_value and initial_value in options:
                index = options.index(initial_value)
            value = st.selectbox(
                label,
                options=options,
                index=index,
                help=help_text
            )
        elif field_type == 'multiselect':
            options = field.get('options', [])
            default = []
            if initial_value:
                if isinstance(initial_value, list):
                    default = initial_value
                elif isinstance(initial_value, str):
                    default = [v.strip() for v in initial_value.split(',')]
            value = st.multiselect(
                label,
                options=options,
                default=default,
                help=help_text
            )
        else:
            # Default to text input
            value = st.text_input(label, value=initial_value, help=help_text)

        form_data[field_name] = value

    return form_data


def render_ai_comparison(original: Dict[str, str], suggested: Dict[str, str]):
    """
    Render side-by-side comparison of original and AI-suggested content.

    Args:
        original: Original content dictionary
        suggested: AI-suggested content dictionary
    """
    st.subheader("AI Suggestions Comparison")

    for field_name, original_value in original.items():
        if field_name in suggested:
            st.markdown(f"**{field_name.replace('_', ' ').title()}**")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Original:**")
                st.info(original_value)

            with col2:
                st.markdown("**AI Suggested:**")
                st.success(suggested[field_name])

            st.markdown("---")


def render_html_preview(submission_data: Dict[str, str],
                       template_path: str = 'templates/preview_template.html'):
    """
    Render HTML preview of a submission.

    Args:
        submission_data: Dictionary containing submission data
        template_path: Path to the preview template
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        template = Template(template_content)
        html = template.render(**submission_data)

        st.components.v1.html(html, height=800, scrolling=True)

    except Exception as e:
        st.error(f"Error rendering preview: {str(e)}")


def render_publication_card(publication, submission_count: int = 0):
    """
    Render a publication card.

    Args:
        publication: Publication object
        submission_count: Number of submissions for this publication
    """
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"### {publication.get_display_name()}")

        with col2:
            render_status_badge(publication.status)

        with col3:
            st.markdown(f"**{submission_count}** submissions")

        st.markdown(f"Created: {format_datetime(publication.created_at)}")

        if publication.published_at:
            st.markdown(f"Published: {format_datetime(publication.published_at)}")


def render_submission_card(submission, fields: Dict[str, str], show_actions: bool = False):
    """
    Render a submission card.

    Args:
        submission: Submission object
        fields: Dictionary of submission fields
        show_actions: Whether to show action buttons
    """
    with st.expander(f"📄 {fields.get('title', 'Untitled')} - {submission.project_name}"):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**Submitted by:** {submission.user_email}")
            st.markdown(f"**Status:** ", end='')
            render_status_badge(submission.status)

        with col2:
            st.markdown(f"**Created:** {format_datetime(submission.created_at)}")

        st.markdown("---")

        # Show field values
        for field_name, field_value in fields.items():
            if field_value:
                st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
                st.write(truncate_text(field_value, 200))

        if show_actions:
            st.markdown("---")
            return st.button(f"Review Submission #{submission.id}", key=f"review_{submission.id}")

    return False


def render_metric_cards(metrics: Dict[str, Any]):
    """
    Render metric cards in columns.

    Args:
        metrics: Dictionary of metrics {label: value}
    """
    cols = st.columns(len(metrics))

    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)


def render_success_message(message: str, icon: str = ""):
    """
    Render a success message.

    Args:
        message: Success message text
        icon: Icon to display (optional)
    """
    st.success(message)


def render_error_message(message: str, icon: str = ""):
    """
    Render an error message.

    Args:
        message: Error message text
        icon: Icon to display (optional)
    """
    st.error(message)


def render_info_message(message: str, icon: str = ""):
    """
    Render an info message.

    Args:
        message: Info message text
        icon: Icon to display (optional)
    """
    st.info(message)


def render_warning_message(message: str, icon: str = ""):
    """
    Render a warning message.

    Args:
        message: Warning message text
        icon: Icon to display (optional)
    """
    st.warning(message)


def render_page_header(title: str, subtitle: str = None, icon: str = None):
    """
    Render a page header with BMS styling.

    Args:
        title: Page title
        subtitle: Optional subtitle
        icon: Optional icon (ignored for professional look)
    """
    st.markdown(
        f'<h1 style="font-family: {FONTS["heading"]}; color: {BMS_COLORS["text_primary"]};">{title}</h1>',
        unsafe_allow_html=True
    )

    if subtitle:
        st.markdown(
            f'<p style="font-family: {FONTS["regular"]}; color: {BMS_COLORS["text_secondary"]}; font-size: 16px;">{subtitle}</p>',
            unsafe_allow_html=True
        )

    st.markdown("---")


def render_sidebar_navigation(user_role: str, user_name: str):
    """
    Render sidebar navigation menu with BMS styling.

    Args:
        user_role: User role ('user' or 'approver')
        user_name: User's name
    """
    st.sidebar.markdown(
        f'<div style="font-family: {FONTS["bold"]}; font-size: 18px; color: {BMS_COLORS["text_primary"]};">Welcome, {user_name}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        f'<div style="font-family: {FONTS["regular"]}; color: {BMS_COLORS["text_secondary"]};">Role: {user_role.title()}</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    # Navigation menu
    if user_role == 'user':
        menu_options = ["New Submission", "My Submissions"]
    else:  # approver
        menu_options = ["Review Queue", "All Publications", "Publish"]

    selected_page = st.sidebar.radio(
        "Navigation",
        menu_options
    )

    st.sidebar.markdown("---")

    return selected_page


def render_confirmation_dialog(message: str, key: str) -> bool:
    """
    Render a confirmation dialog.

    Args:
        message: Confirmation message
        key: Unique key for the button

    Returns:
        True if confirmed, False otherwise
    """
    st.warning(message)
    col1, col2 = st.columns([1, 4])

    with col1:
        confirmed = st.button("Confirm", key=f"{key}_confirm", type="primary")

    with col2:
        cancelled = st.button("Cancel", key=f"{key}_cancel")

    return confirmed


def render_project_selector(projects: List[str] = None, allow_custom: bool = True) -> str:
    """
    Render a project name input (manual entry only for BMS).

    Args:
        projects: List of available project names (ignored if None)
        allow_custom: Whether to allow custom project names

    Returns:
        Entered project name
    """
    # Always use manual text input for BMS
    project_name = st.text_input(
        "Project Name *",
        placeholder="Enter your project name",
        help="Enter the name of the project for this spotlight"
    )

    return project_name


def render_loading_spinner(message: str = "Loading..."):
    """
    Render a loading spinner with message.

    Args:
        message: Loading message
    """
    return st.spinner(message)
