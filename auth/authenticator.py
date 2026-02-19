"""
Authentication module for Streamlit application.
Handles user login, logout, and session management.
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
from typing import Optional, Dict, Any
import streamlit_authenticator as stauth


class Authenticator:
    """Handles authentication for the Streamlit application."""

    def __init__(self, config_path: str = 'config/users.yaml'):
        """
        Initialize the authenticator.

        Args:
            config_path: Path to the users configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.authenticator = self._create_authenticator()

    def _load_config(self) -> Dict[str, Any]:
        """Load the authentication configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except FileNotFoundError:
            st.error(f"Configuration file not found: {self.config_path}")
            return {}

    def _create_authenticator(self) -> stauth.Authenticate:
        """Create the streamlit-authenticator instance."""
        if not self.config:
            return None

        return stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days']
        )

    def login(self, location: str = 'main') -> tuple:
        """
        Display login form and handle authentication.

        Args:
            location: Where to display the login form ('main' or 'sidebar')

        Returns:
            Tuple of (name, authentication_status, username)
        """
        if self.authenticator is None:
            st.error("Authenticator not properly configured")
            return None, None, None

        name, authentication_status, username = self.authenticator.login(
            location=location
        )

        # Store user info in session state
        if authentication_status:
            user_data = self.config['credentials']['usernames'].get(username, {})
            st.session_state['user_email'] = user_data.get('email', username)
            st.session_state['user_name'] = name
            st.session_state['user_role'] = user_data.get('role', 'user')
            st.session_state['username'] = username

        return name, authentication_status, username

    def logout(self, location: str = 'sidebar'):
        """
        Display logout button.

        Args:
            location: Where to display the logout button ('main' or 'sidebar')
        """
        if self.authenticator:
            self.authenticator.logout(location=location)

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user information.

        Returns:
            Dictionary with user information or None if not authenticated
        """
        if 'authentication_status' not in st.session_state:
            return None

        if not st.session_state.get('authentication_status'):
            return None

        return {
            'email': st.session_state.get('user_email'),
            'name': st.session_state.get('user_name'),
            'role': st.session_state.get('user_role'),
            'username': st.session_state.get('username')
        }

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return st.session_state.get('authentication_status', False)

    def is_approver(self) -> bool:
        """Check if current user has approver role."""
        return st.session_state.get('user_role') == 'approver'

    def require_authentication(self):
        """Require authentication, show login if not authenticated."""
        if not self.is_authenticated():
            st.warning("Please login to continue")
            return False
        return True

    def require_approver_role(self):
        """Require approver role, show error if user is not an approver."""
        if not self.is_authenticated():
            st.error("Please login to continue")
            return False

        if not self.is_approver():
            st.error("You do not have permission to access this page")
            return False

        return True


def init_session_state():
    """Initialize session state variables."""
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None

    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = None

    if 'user_name' not in st.session_state:
        st.session_state['user_name'] = None

    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None

    if 'username' not in st.session_state:
        st.session_state['username'] = None


def get_user_display_name() -> str:
    """Get the display name of the current user."""
    name = st.session_state.get('user_name', 'User')
    role = st.session_state.get('user_role', '')

    if role:
        return f"{name} ({role.title()})"
    return name
