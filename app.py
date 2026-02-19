"""
Main Streamlit application for Organizational Spotlight.

This application manages bi-monthly organizational spotlight publications
with a two-role workflow (Users and Approvers).
"""

import streamlit as st
from pathlib import Path

# Import configuration
from config import settings

# Import authentication
from auth.simple_auth import SimpleAuthenticator
from auth.authenticator import init_session_state, get_user_display_name

# Import database
from database.db_manager import DatabaseManager
from database.init_db import initialize_database

# Import UI components
from ui.user_dashboard import show_user_dashboard
from ui.approver_dashboard import show_approver_dashboard
from ui.bms_styles import load_custom_css, render_bms_header, render_bms_sidebar_header


def main():
    """Main application entry point."""

    # Configure page
    st.set_page_config(**settings.PAGE_CONFIG)

    # Load custom CSS and BMS branding
    load_custom_css()

    # Initialize session state
    init_session_state()

    # Initialize database if it doesn't exist
    db_path = Path(settings.DATABASE_PATH)
    if not db_path.exists():
        with st.spinner("Initializing database..."):
            initialize_database(settings.DATABASE_PATH)

    # Initialize database manager
    db_manager = DatabaseManager(settings.DATABASE_PATH)

    # Initialize authenticator
    auth = SimpleAuthenticator()

    # Show BMS branded header
    render_bms_header(settings.APP_NAME, "Managing bi-monthly organizational achievements")

    # Authentication
    if not auth.is_authenticated():
        # Show login form
        st.markdown("### Please Login")

        # Show help text before login form
        with st.expander("Default Login Credentials (Demo)"):
            st.markdown("""
            **User Account:**
            - Username: `user1`
            - Password: `password123`

            **Approver Account:**
            - Username: `approver1`
            - Password: `password123`

            **Note:** In production, these should be replaced with SSO/OAuth authentication.
            """)

        name, authentication_status, username = auth.login()

        if authentication_status is False:
            st.error("Username/password is incorrect")

        return

    # User is authenticated
    current_user = auth.get_current_user()

    if current_user is None:
        st.error("Authentication error. Please try logging in again.")
        return

    # Update last login time
    db_manager.update_user_last_login(current_user['email'])

    # Show user info in sidebar with BMS styling
    render_bms_sidebar_header(
        current_user['name'],
        current_user['role'],
        current_user['email']
    )

    # Logout button
    if st.sidebar.button("Logout", type="primary"):
        auth.logout()
        st.rerun()

    st.sidebar.markdown("---")

    # Route to appropriate dashboard based on role
    if current_user['role'] == 'approver':
        show_approver_dashboard(
            db_manager,
            current_user['email'],
            current_user['name']
        )
    else:  # user
        show_user_dashboard(
            db_manager,
            current_user['email'],
            current_user['name']
        )

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='text-align: center; color: #7F8C8D; font-size: 11px;'>"
        "Bristol Myers Squibb<br>"
        "Organizational Spotlight<br>"
        "v1.0.0"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
