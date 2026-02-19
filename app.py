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
from auth.authenticator import Authenticator, init_session_state, get_user_display_name

# Import database
from database.db_manager import DatabaseManager
from database.init_db import initialize_database

# Import UI components
from ui.user_dashboard import show_user_dashboard
from ui.approver_dashboard import show_approver_dashboard


def main():
    """Main application entry point."""

    # Configure page
    st.set_page_config(**settings.PAGE_CONFIG)

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
    auth = Authenticator()

    # Show title
    st.title(f"✨ {settings.APP_NAME}")

    # Authentication
    if not auth.is_authenticated():
        # Show login form
        st.markdown("---")
        st.markdown("### Please Login")

        name, authentication_status, username = auth.login('main')

        if authentication_status is False:
            st.error("Username/password is incorrect")
        elif authentication_status is None:
            st.info("Please enter your username and password")

            # Show help text
            with st.expander("ℹ️ Default Login Credentials (Demo)"):
                st.markdown("""
                **User Account:**
                - Username: `user1`
                - Password: `password123`

                **Approver Account:**
                - Username: `approver1`
                - Password: `password123`

                **Note:** In production, these should be replaced with SSO/OAuth authentication.
                """)

        return

    # User is authenticated
    current_user = auth.get_current_user()

    if current_user is None:
        st.error("Authentication error. Please try logging in again.")
        return

    # Update last login time
    db_manager.update_user_last_login(current_user['email'])

    # Show user info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 👤 {current_user['name']}")
    st.sidebar.markdown(f"**Role:** {current_user['role'].title()}")
    st.sidebar.markdown(f"**Email:** {current_user['email']}")
    st.sidebar.markdown("---")

    # Logout button
    if st.sidebar.button("🚪 Logout", type="primary"):
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
        f"<div style='text-align: center; color: #666; font-size: 12px;'>"
        f"{settings.APP_NAME}<br>v1.0.0"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
