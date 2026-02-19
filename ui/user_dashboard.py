"""
User dashboard for submitting organizational spotlights.
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime

from database.db_manager import DatabaseManager
from services.ai_service import get_ai_service
from services.publication_service import PublicationService
from config import settings
from utils.validators import validate_form_submission, validate_project_name
from ui.components import (
    render_page_header, render_submission_form, render_ai_comparison,
    render_html_preview, render_project_selector, render_success_message,
    render_error_message, render_info_message, render_status_badge,
    render_submission_card, render_loading_spinner, render_metric_cards
)


def show_user_dashboard(db_manager: DatabaseManager, user_email: str, user_name: str):
    """
    Display the main user dashboard.

    Args:
        db_manager: Database manager instance
        user_email: Current user's email
        user_name: Current user's name
    """
    # Initialize services
    pub_service = PublicationService(db_manager)
    ai_service = get_ai_service()

    # Ensure current year publications exist
    pub_service.ensure_current_year_publications()

    # Sidebar navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Choose a page",
        ["New Submission", "My Submissions"],
        label_visibility="collapsed"
    )

    if page == "New Submission":
        show_new_submission_page(db_manager, pub_service, ai_service, user_email, user_name)
    elif page == "My Submissions":
        show_my_submissions_page(db_manager, user_email)


def show_new_submission_page(db_manager: DatabaseManager,
                             pub_service: PublicationService,
                             ai_service,
                             user_email: str,
                             user_name: str):
    """
    Display the new submission page.

    Args:
        db_manager: Database manager instance
        pub_service: Publication service instance
        ai_service: AI service instance
        user_email: Current user's email
        user_name: Current user's name
    """
    render_page_header(
        "Submit Organizational Spotlight",
        "Share your team's achievements and make them shine"
    )

    # Get active publication
    active_pub = pub_service.get_active_publication()

    if not active_pub:
        render_error_message(
            "No active publication period available. Please check back later."
        )
        return

    # Show active publication info
    st.info(f"Submitting for: **{active_pub.get_display_name()}**")

    # Initialize session state for form
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

    if 'ai_suggestions' not in st.session_state:
        st.session_state.ai_suggestions = None

    if 'show_preview' not in st.session_state:
        st.session_state.show_preview = False

    # Step 1: Project Selection
    st.markdown("## Step 1: Select Project")
    project_name = render_project_selector(settings.PROJECT_NAMES)

    if not project_name:
        st.warning("Please select or enter a project name to continue.")
        return

    # Step 2: Fill Form
    st.markdown("## Step 2: Fill Submission Details")
    st.markdown("*Fields marked with * are required*")

    form_data = render_submission_form(
        settings.FORM_FIELDS,
        st.session_state.form_data
    )

    # Update session state
    st.session_state.form_data = form_data

    st.markdown("---")

    # Step 3: AI Suggestions (Optional)
    st.markdown("## Step 3: Get AI Suggestions (Optional)")
    st.markdown("Let AI help improve your submission for maximum impact!")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("Get AI Suggestions", type="primary"):
            # Validate form first
            is_valid, errors = validate_form_submission(form_data, settings.FORM_FIELDS)

            if not is_valid:
                render_error_message("Please fix the following errors:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Prepare submission data
                submission_data = {
                    'project_name': project_name,
                    **form_data
                }

                # Get AI suggestions
                with render_loading_spinner("Generating AI suggestions..."):
                    suggestions = ai_service.generate_suggestions(submission_data)

                    if suggestions:
                        st.session_state.ai_suggestions = suggestions
                        render_success_message("AI suggestions generated successfully!")
                    else:
                        render_error_message("Failed to generate AI suggestions. Please try again.")

    # Show AI suggestions comparison
    if st.session_state.ai_suggestions:
        st.markdown("### Review AI Suggestions")

        # Create comparison for relevant fields
        original = {k: v for k, v in form_data.items()
                   if k in st.session_state.ai_suggestions and v}

        render_ai_comparison(original, st.session_state.ai_suggestions)

        # Accept suggestions
        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            if st.button("Accept Suggestions", type="primary"):
                # Update form data with suggestions
                for key, value in st.session_state.ai_suggestions.items():
                    if key in st.session_state.form_data:
                        st.session_state.form_data[key] = value

                render_success_message("Suggestions accepted! Scroll up to see updated content.")
                st.rerun()

        with col2:
            if st.button("Reject Suggestions"):
                st.session_state.ai_suggestions = None
                render_info_message("Suggestions rejected. Using your original content.")
                st.rerun()

    st.markdown("---")

    # Step 4: Preview
    st.markdown("## Step 4: Preview Your Submission")

    if st.button("Preview", type="secondary"):
        st.session_state.show_preview = True

    if st.session_state.show_preview:
        preview_data = {
            'project_name': project_name,
            **st.session_state.form_data
        }
        render_html_preview(preview_data)

    st.markdown("---")

    # Step 5: Submit
    st.markdown("## Step 5: Submit")

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        submit_button = st.button("Submit", type="primary")

    with col2:
        save_draft_button = st.button("Save as Draft")

    if submit_button or save_draft_button:
        # Validate form
        is_valid, errors = validate_form_submission(form_data, settings.FORM_FIELDS)

        # Validate project name
        proj_valid, proj_error = validate_project_name(project_name, settings.PROJECT_NAMES)

        if not proj_valid:
            errors.append(proj_error)
            is_valid = False

        if not is_valid:
            render_error_message("Please fix the following errors:")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Create submission
            try:
                submission = db_manager.create_submission(
                    publication_id=active_pub.id,
                    user_email=user_email,
                    project_name=project_name,
                    fields=form_data
                )

                # Update status based on button clicked
                status = 'submitted' if submit_button else 'draft'
                db_manager.update_submission_status(submission.id, status)

                # Save AI suggestions if they were generated and accepted
                if st.session_state.ai_suggestions:
                    original_content = {
                        'project_name': project_name,
                        **form_data
                    }
                    db_manager.save_ai_suggestion(
                        submission.id,
                        original_content,
                        st.session_state.ai_suggestions,
                        accepted=True
                    )

                # Clear session state
                st.session_state.form_data = {}
                st.session_state.ai_suggestions = None
                st.session_state.show_preview = False

                if submit_button:
                    render_success_message(
                        f"Submission #{submission.id} submitted successfully! "
                        "Your spotlight will be reviewed by an approver."
                    )
                else:
                    render_success_message(
                        f"Draft #{submission.id} saved successfully! "
                        "You can continue editing it later."
                    )

                st.balloons()

            except Exception as e:
                render_error_message(f"Failed to create submission: {str(e)}")


def show_my_submissions_page(db_manager: DatabaseManager, user_email: str):
    """
    Display the user's submissions page.

    Args:
        db_manager: Database manager instance
        user_email: Current user's email
    """
    render_page_header(
        "My Submissions",
        "View and manage your spotlight submissions"
    )

    # Get user's submissions
    submissions = db_manager.get_submissions_by_user(user_email)

    if not submissions:
        render_info_message("You haven't created any submissions yet.")
        return

    # Show metrics
    status_counts = {
        'draft': 0,
        'submitted': 0,
        'approved': 0,
        'rejected': 0
    }

    for sub in submissions:
        if sub.status in status_counts:
            status_counts[sub.status] += 1

    render_metric_cards({
        "Total": len(submissions),
        "Drafts": status_counts['draft'],
        "Submitted": status_counts['submitted'],
        "Approved": status_counts['approved'],
        "Rejected": status_counts['rejected']
    })

    st.markdown("---")

    # Filter by status
    filter_status = st.selectbox(
        "Filter by status",
        options=['All', 'Draft', 'Submitted', 'Approved', 'Rejected']
    )

    # Display submissions
    for submission in submissions:
        if filter_status != 'All' and submission.status != filter_status.lower():
            continue

        # Get submission fields
        fields = db_manager.get_submission_fields(submission.id)

        # Get publication info
        publication = db_manager.get_publication(submission.publication_id)

        with st.expander(
            f"{fields.get('title', 'Untitled')} - {submission.project_name}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Publication:** {publication.get_display_name()}")
                st.markdown(f"**Status:** ", end='')
                render_status_badge(submission.status)

            with col2:
                st.markdown(f"**Created:** {submission.created_at.strftime('%Y-%m-%d %H:%M')}")
                if submission.submitted_at:
                    st.markdown(f"**Submitted:** {submission.submitted_at.strftime('%Y-%m-%d %H:%M')}")

            st.markdown("---")

            # Show fields
            for field_name, field_value in fields.items():
                if field_value:
                    st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
                    st.write(field_value)

            # Action buttons for drafts
            if submission.status == 'draft':
                st.markdown("---")
                col1, col2 = st.columns([1, 4])

                with col1:
                    if st.button("Edit", key=f"edit_{submission.id}"):
                        st.info("Edit functionality will be implemented in the next version.")

                with col2:
                    if st.button("Delete", key=f"delete_{submission.id}"):
                        st.warning("Delete functionality will be implemented in the next version.")
