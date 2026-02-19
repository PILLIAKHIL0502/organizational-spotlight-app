"""
Email service for sending publication emails via SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from jinja2 import Template
import streamlit as st

from config import settings
from database.models import Submission, Publication


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        """Initialize the email service."""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_email = settings.SMTP_EMAIL
        self.smtp_password = settings.SMTP_PASSWORD

    def render_email_html(self, publication: Publication,
                         submissions: List[Dict[str, Any]],
                         template_path: str = 'templates/email_template.html') -> str:
        """
        Render the email HTML from template.

        Args:
            publication: Publication object
            submissions: List of submission dictionaries with fields
            template_path: Path to the email template file

        Returns:
            Rendered HTML string
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            template = Template(template_content)

            html = template.render(
                publication=publication,
                submissions=submissions,
                publication_name=publication.get_display_name()
            )

            return html

        except Exception as e:
            st.error(f"Error rendering email template: {str(e)}")
            raise

    def send_email(self, recipients: List[str], subject: str,
                  html_content: str, text_content: str = None) -> bool:
        """
        Send an email via SMTP.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional fallback)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.smtp_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject

            # Add plain text part (fallback)
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            else:
                # Generate simple text version from HTML
                text_part = MIMEText('Please view this email in HTML format.', 'plain')
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(message)

            return True

        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
            return False

    def send_publication_email(self, publication: Publication,
                              submissions: List[Dict[str, Any]],
                              recipients: List[str] = None) -> bool:
        """
        Send a publication email with approved submissions.

        Args:
            publication: Publication object
            submissions: List of approved submission dictionaries
            recipients: List of recipient emails (uses default if None)

        Returns:
            True if email sent successfully, False otherwise
        """
        if recipients is None:
            recipients = settings.EMAIL_RECIPIENTS

        # Prepare email subject
        subject = f"📰 {publication.get_display_name()} - Organizational Spotlight"

        # Render HTML content
        try:
            html_content = self.render_email_html(publication, submissions)
        except Exception as e:
            st.error(f"Failed to render email: {str(e)}")
            return False

        # Send email
        return self.send_email(recipients, subject, html_content)

    def send_test_email(self, recipient: str) -> bool:
        """
        Send a test email to verify SMTP configuration.

        Args:
            recipient: Recipient email address

        Returns:
            True if test email sent successfully, False otherwise
        """
        subject = "Test Email - Organizational Spotlight"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>Test Email</h2>
                <p>This is a test email from the Organizational Spotlight application.</p>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
            </body>
        </html>
        """
        text_content = "Test Email - If you received this, your SMTP configuration is working!"

        return self.send_email([recipient], subject, html_content, text_content)

    def validate_email_structure(self, html_content: str) -> bool:
        """
        Validate that the email HTML structure is valid.

        Args:
            html_content: HTML content to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check for required HTML tags
        required_tags = ['<html', '<body', '</body>', '</html>']

        for tag in required_tags:
            if tag.lower() not in html_content.lower():
                return False

        return True


# Singleton instance
_email_service_instance = None


def get_email_service() -> EmailService:
    """
    Get the singleton email service instance.

    Returns:
        EmailService instance
    """
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
