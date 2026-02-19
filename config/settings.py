"""
Application configuration and settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Application settings
APP_NAME = os.getenv('APP_NAME', 'Organizational Spotlight')
DATABASE_PATH = os.getenv('DATABASE_PATH', './database/spotlight.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# AWS Bedrock settings
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BEDROCK_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'

# SMTP settings
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.office365.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# OAuth settings (optional)
OAUTH_CLIENT_ID = os.getenv('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('OAUTH_CLIENT_SECRET')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:8501/oauth/callback')

# Form field configuration
# This can be customized based on user requirements
FORM_FIELDS = [
    {
        'name': 'title',
        'label': 'Spotlight Title',
        'type': 'text',
        'required': True,
        'placeholder': 'Enter a compelling title for your spotlight',
        'help_text': 'A brief, attention-grabbing title (50-80 characters recommended)'
    },
    {
        'name': 'description',
        'label': 'Description',
        'type': 'textarea',
        'required': True,
        'placeholder': 'Describe what this spotlight is about',
        'help_text': 'Provide context and background (2-3 sentences)'
    },
    {
        'name': 'key_achievements',
        'label': 'Key Achievements',
        'type': 'textarea',
        'required': True,
        'placeholder': 'List the main accomplishments',
        'help_text': 'Highlight the most important achievements and milestones'
    },
    {
        'name': 'impact',
        'label': 'Impact & Results',
        'type': 'textarea',
        'required': True,
        'placeholder': 'Describe the impact and measurable results',
        'help_text': 'Include metrics, outcomes, and business value delivered'
    },
    {
        'name': 'category',
        'label': 'Category',
        'type': 'select',
        'required': True,
        'options': [
            'Innovation',
            'Process Improvement',
            'Customer Success',
            'Team Achievement',
            'Technology Advancement',
            'Business Growth',
            'Other'
        ],
        'help_text': 'Select the category that best fits this spotlight'
    },
    {
        'name': 'tags',
        'label': 'Tags',
        'type': 'multiselect',
        'required': False,
        'options': [
            'Digital Transformation',
            'AI/ML',
            'Cloud',
            'Security',
            'Data Analytics',
            'Automation',
            'Collaboration',
            'Customer Experience',
            'Efficiency',
            'Cost Savings'
        ],
        'help_text': 'Select relevant tags (optional)'
    },
    {
        'name': 'team_members',
        'label': 'Team Members',
        'type': 'text',
        'required': False,
        'placeholder': 'Names of key contributors (comma-separated)',
        'help_text': 'Recognize team members who contributed to this achievement'
    }
]

# Project names configuration
# Set to None to use manual text input only
PROJECT_NAMES = None  # Manual population only

# Email recipients configuration
# Can be a list of email addresses or groups
EMAIL_RECIPIENTS = [
    'all-staff@organization.com',
    'leadership@organization.com',
]

# AI prompt template
AI_PROMPT_TEMPLATE = """You are helping improve organizational spotlight submissions for internal communications.

Given the following submission, enhance it to:
1. Improve clarity and readability
2. Highlight key achievements and impact more effectively
3. Use professional, engaging language appropriate for company-wide communications
4. Keep it concise while maintaining all important details
5. Ensure the tone is positive and celebrates the achievement

Original submission:
Project: {project_name}
Title: {title}
Description: {description}
Key Achievements: {key_achievements}
Impact & Results: {impact}
Category: {category}

Please provide an improved version of the Title, Description, Key Achievements, and Impact & Results sections.
Return your response in JSON format with these exact keys: "title", "description", "key_achievements", "impact".
"""

# Streamlit page configuration
PAGE_CONFIG = {
    'page_title': 'BMS - ' + APP_NAME,
    'page_icon': 'assets/bms.png',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}
