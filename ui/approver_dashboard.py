"""
Approver dashboard for reviewing and publishing organizational spotlights.
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

from database.db_manager import DatabaseManager
from services.ai_service import get_ai_service
from services.publication_service import PublicationService
from services.email_service import get_email_service
from config import settings
from utils.validators import validate_form_submission
from ui.components import (
    render_page_header, render_submission_form, render_ai_comparison,
    render_html_preview, render_success_message, render_error_message,
    render_info_message, render_status_badge, render_metric_cards,
    render_loading_spinner, render_confirmation_dialog
)


def show_approver_dashboard(db_manager: DatabaseManager, user_email: str, user_name: str):
    """
    Display the main approver dashboard.

    Args:
        db_manager: Database manager instance
        user_email: Current user's email
        user_name: Current user's name
    """
    # Initialize services
    pub_service = PublicationService(db_manager)

    # Sidebar navigation
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Choose a page",
        ["Review Queue", "All Publications", "Publish"],
        label_visibility="collapsed"
    )

    if page == "Review Queue":
        show_review_queue_page(db_manager, pub_service, user_email)
    elif page == "All Publications":
        show_all_publications_page(db_manager, pub_service)
    elif page == "Publish":
        show_publish_page(db_manager, pub_service, user_email)


def show_review_queue_page(db_manager: DatabaseManager,
                           pub_service: PublicationService,
                           user_email: str):
    """
    Display the review queue page.

    Args:
        db_manager: Database manager instance
        pub_service: Publication service instance
        user_email: Current user's email
    """
    render_page_header(
        "Review Queue",
        "Review submitted spotlights and approve for publication"
    )

    # Get all publications with submitted items
    all_pubs = pub_service.get_all_publications()

    # Filter publications with submissions
    pubs_with_submissions = []
    for pub in all_pubs:
        submitted = db_manager.get_submissions_by_publication(pub.id, status='submitted')
        if submitted:
            pubs_with_submissions.append((pub, len(submitted)))

    if not pubs_with_submissions:
        render_info_message("No submissions awaiting review.")
        return

    # Select publication
    pub_options = {f"{pub.get_display_name()} ({count} pending)": pub.id
                   for pub, count in pubs_with_submissions}

    selected_pub_name = st.selectbox(
        "Select Publication",
        options=list(pub_options.keys())
    )

    selected_pub_id = pub_options[selected_pub_name]
    selected_pub = pub_service.get_publication_by_id(selected_pub_id)

    # Get submitted submissions
    submissions = db_manager.get_submissions_by_publication(selected_pub_id, status='submitted')

    if not submissions:
        render_info_message("No submissions to review for this publication.")
        return

    st.markdown(f"### {len(submissions)} Submissions Awaiting Review")

    # Display submissions
    for idx, submission in enumerate(submissions):
        fields = db_manager.get_submission_fields(submission.id)

        with st.expander(
            f"Submission #{submission.id}: {fields.get('title', 'Untitled')}",
            expanded=(idx == 0)
        ):
            show_submission_review(
                db_manager,
                submission,
                fields,
                user_email
            )


def show_submission_review(db_manager: DatabaseManager,
                          submission,
                          fields: Dict[str, str],
                          reviewer_email: str):
    """
    Display submission review interface.

    Args:
        db_manager: Database manager instance
        submission: Submission object
        fields: Submission fields dictionary
        reviewer_email: Reviewer's email
    """
    # Show submission details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Project:** {submission.project_name}")
        st.markdown(f"**Submitted by:** {submission.user_email}")

    with col2:
        st.markdown(f"**Submitted:** {submission.submitted_at.strftime('%Y-%m-%d %H:%M')}")

    st.markdown("---")

    # Display fields
    for field_name, field_value in fields.items():
        if field_value:
            st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
            st.write(field_value)

    st.markdown("---")

    # Edit option
    if st.checkbox(f"Edit Submission", key=f"edit_check_{submission.id}"):
        st.markdown("### Edit Submission")

        # Allow editing
        edited_fields = render_submission_form(settings.FORM_FIELDS, fields)

        # Get AI suggestions for edited content
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("Get AI Suggestions", key=f"ai_{submission.id}"):
                ai_service = get_ai_service()

                submission_data = {
                    'project_name': submission.project_name,
                    **edited_fields
                }

                with render_loading_spinner("Generating AI suggestions..."):
                    suggestions = ai_service.generate_suggestions(submission_data)

                    if suggestions:
                        st.session_state[f'ai_suggestions_{submission.id}'] = suggestions
                        render_success_message("AI suggestions generated!")
                        st.rerun()

        # Show AI suggestions if available
        if f'ai_suggestions_{submission.id}' in st.session_state:
            original = {k: v for k, v in edited_fields.items()
                       if k in st.session_state[f'ai_suggestions_{submission.id}'] and v}

            render_ai_comparison(original, st.session_state[f'ai_suggestions_{submission.id}'])

            if st.button("Accept AI Suggestions", key=f"accept_ai_{submission.id}", type="primary"):
                for key, value in st.session_state[f'ai_suggestions_{submission.id}'].items():
                    if key in edited_fields:
                        edited_fields[key] = value

                render_success_message("Suggestions accepted!")

        # Save edited fields
        if st.button("Save Changes", key=f"save_{submission.id}"):
            try:
                db_manager.update_submission_fields(submission.id, edited_fields)
                render_success_message("Changes saved successfully!")
                st.rerun()
            except Exception as e:
                render_error_message(f"Failed to save changes: {str(e)}")

    # Preview
    if st.button("Preview", key=f"preview_{submission.id}"):
        st.session_state[f'show_preview_{submission.id}'] = True

    if st.session_state.get(f'show_preview_{submission.id}', False):
        preview_data = {
            'project_name': submission.project_name,
            **fields
        }
        render_html_preview(preview_data)

    st.markdown("---")

    # Approve/Reject buttons
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        approve_button = st.button(
            "Approve",
            key=f"approve_{submission.id}",
            type="primary"
        )

    with col2:
        reject_button = st.button(
            "Reject",
            key=f"reject_{submission.id}"
        )

    if approve_button:
        try:
            db_manager.update_submission_status(
                submission.id,
                'approved',
                reviewed_by=reviewer_email
            )
            render_success_message(f"Submission #{submission.id} approved!")
            st.rerun()
        except Exception as e:
            render_error_message(f"Failed to approve submission: {str(e)}")

    if reject_button:
        reason = st.text_area(
            "Rejection reason (optional)",
            key=f"reject_reason_{submission.id}",
            placeholder="Provide feedback to the submitter..."
        )

        if st.button("Confirm Rejection", key=f"confirm_reject_{submission.id}"):
            try:
                db_manager.update_submission_status(
                    submission.id,
                    'rejected',
                    reviewed_by=reviewer_email
                )
                render_success_message(f"Submission #{submission.id} rejected.")
                st.rerun()
            except Exception as e:
                render_error_message(f"Failed to reject submission: {str(e)}")


def show_all_publications_page(db_manager: DatabaseManager,
                               pub_service: PublicationService):
    """
    Display all publications page.

    Args:
        db_manager: Database manager instance
        pub_service: Publication service instance
    """
    render_page_header(
        "All Publications",
        "View and manage all publication cycles"
    )

    # Year filter
    current_year = datetime.now().year
    year_options = [current_year - 1, current_year, current_year + 1]
    selected_year = st.selectbox("Filter by year", options=year_options, index=1)

    # Get publications for selected year
    publications = pub_service.get_all_publications(selected_year)

    if not publications:
        render_info_message(f"No publications found for {selected_year}.")
        return

    # Display publications
    for pub in publications:
        stats = pub_service.get_publication_stats(pub.id)

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 2])

            with col1:
                st.markdown(f"### {pub.get_display_name()}")

            with col2:
                render_status_badge(pub.status)

            with col3:
                st.markdown(f"**Total Submissions:** {stats['total']}")

            # Show detailed stats
            if stats['total'] > 0:
                metric_data = {
                    "Draft": stats['draft'],
                    "Submitted": stats['submitted'],
                    "Approved": stats['approved'],
                    "Rejected": stats['rejected']
                }
                render_metric_cards(metric_data)

            st.markdown("---")


def show_publish_page(db_manager: DatabaseManager,
                     pub_service: PublicationService,
                     user_email: str):
    """
    Display the publish page.

    Args:
        db_manager: Database manager instance
        pub_service: Publication service instance
        user_email: Current user's email
    """
    render_page_header(
        "Publish Spotlights",
        "Review and send approved spotlights via email"
    )

    # Get publications with approved submissions
    all_pubs = pub_service.get_all_publications()

    pubs_ready = []
    for pub in all_pubs:
        if pub.status in ['open', 'under_review']:
            approved = db_manager.get_submissions_by_publication(pub.id, status='approved')
            if approved:
                pubs_ready.append((pub, len(approved)))

    if not pubs_ready:
        render_info_message("No publications with approved submissions ready to publish.")
        return

    # Select publication
    pub_options = {f"{pub.get_display_name()} ({count} approved)": pub.id
                   for pub, count in pubs_ready}

    selected_pub_name = st.selectbox(
        "Select Publication to Publish",
        options=list(pub_options.keys())
    )

    selected_pub_id = pub_options[selected_pub_name]
    selected_pub = pub_service.get_publication_by_id(selected_pub_id)

    # Get approved submissions
    approved_submissions = db_manager.get_submissions_by_publication(
        selected_pub_id,
        status='approved'
    )

    st.markdown(f"### {len(approved_submissions)} Approved Submissions")

    # Display approved submissions
    submissions_data = []

    for submission in approved_submissions:
        fields = db_manager.get_submission_fields(submission.id)

        submissions_data.append({
            'project_name': submission.project_name,
            **fields
        })

        with st.expander(f"{fields.get('title', 'Untitled')} - {submission.project_name}"):
            for field_name, field_value in fields.items():
                if field_value:
                    st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
                    st.write(field_value)

    st.markdown("---")

    # Email configuration
    st.markdown("### Email Configuration")

    recipients_input = st.text_area(
        "Recipients (comma-separated emails)",
        value=", ".join(settings.EMAIL_RECIPIENTS),
        help="Enter email addresses separated by commas"
    )

    recipients = [email.strip() for email in recipients_input.split(',') if email.strip()]

    # Preview email
    if st.button("Preview Email"):
        st.markdown("### Email Preview")

        email_service = get_email_service()

        try:
            html_content = email_service.render_email_html(
                selected_pub,
                submissions_data
            )

            st.components.v1.html(html_content, height=800, scrolling=True)

        except Exception as e:
            render_error_message(f"Failed to render email preview: {str(e)}")

    st.markdown("---")

    # Publish button
    st.markdown("### Publish and Send")

    st.warning(
        f"This will:\n"
        f"1. Mark the publication as 'published'\n"
        f"2. Send email to {len(recipients)} recipient(s)\n"
        f"3. Lock the publication (no more edits)"
    )

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("Publish & Send", type="primary"):
            st.session_state['confirm_publish'] = True

    with col2:
        if st.button("Cancel"):
            st.session_state['confirm_publish'] = False

    if st.session_state.get('confirm_publish', False):
        st.markdown("### Confirm Publication")

        if st.button("Yes, Publish Now", type="primary"):
            email_service = get_email_service()

            with render_loading_spinner("Publishing and sending email..."):
                try:
                    # Send email
                    email_sent = email_service.send_publication_email(
                        selected_pub,
                        submissions_data,
                        recipients
                    )

                    if email_sent:
                        # Update publication status
                        pub_service.publish_publication(selected_pub_id)

                        st.session_state['confirm_publish'] = False

                        render_success_message(
                            f"Publication '{selected_pub.get_display_name()}' "
                            f"published successfully and email sent to {len(recipients)} recipient(s)!"
                        )

                        st.balloons()

                    else:
                        render_error_message(
                            "Failed to send email. Publication not marked as published."
                        )

                except Exception as e:
                    render_error_message(f"Error during publication: {str(e)}")
