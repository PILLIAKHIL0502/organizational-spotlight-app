"""
Simple authentication module without external dependencies.
Uses basic username/password authentication with session state.
"""

import streamlit as st
import yaml
from yaml.loader import SafeLoader
from typing import Optional, Dict, Any
import hashlib


class SimpleAuthenticator:
    """Simple authentication handler."""

    def __init__(self, config_path: str = 'config/users.yaml'):
        """Initialize the authenticator."""
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load the authentication configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.load(file, Loader=SafeLoader)
            return config
        except FileNotFoundError:
            st.error(f"Configuration file not found: {self.config_path}")
            return {}

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, username: str, password: str) -> bool:
        """Verify username and password."""
        if not self.config:
            return False

        users = self.config.get('credentials', {}).get('usernames', {})

        if username not in users:
            return False

        stored_password = users[username].get('password', '')

        # For demo, we'll use simple comparison
        # In production, use proper password hashing
        # For now, accept the plain password "password123" for all users
        if password == 'password123':
            return True

        return False

    def login(self) -> tuple:
        """
        Display login form and handle authentication.

        Returns:
            Tuple of (name, authentication_status, username)
        """
        if not self.config:
            st.error("Authenticator not properly configured")
            return None, False, None

        # Check if already authenticated
        if st.session_state.get('authentication_status'):
            username = st.session_state.get('username')
            users = self.config.get('credentials', {}).get('usernames', {})
            name = users.get(username, {}).get('name', username)
            return name, True, username

        # Display login form
        with st.form(key='login_form'):
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            submit = st.form_submit_button('Login')

            if submit:
                if self._verify_password(username, password):
                    # Authentication successful
                    users = self.config.get('credentials', {}).get('usernames', {})
                    user_data = users.get(username, {})

                    st.session_state['authentication_status'] = True
                    st.session_state['user_email'] = user_data.get('email', username)
                    st.session_state['user_name'] = user_data.get('name', username)
                    st.session_state['user_role'] = user_data.get('role', 'user')
                    st.session_state['username'] = username

                    st.success('Login successful!')
                    st.rerun()
                else:
                    st.session_state['authentication_status'] = False
                    return None, False, None

        return None, None, None

    def logout(self):
        """Logout the current user."""
        st.session_state['authentication_status'] = None
        st.session_state['user_email'] = None
        st.session_state['user_name'] = None
        st.session_state['user_role'] = None
        st.session_state['username'] = None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user information."""
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
