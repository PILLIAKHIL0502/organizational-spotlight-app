# Organizational Spotlight Application

A comprehensive Streamlit-based web application for managing bi-monthly organizational spotlight publications. The application features a two-role workflow (Users and Approvers) with AI-powered content enhancement, preview capabilities, and automated email distribution.

## Features

### For Users
- ✏️ Submit organizational spotlights for bi-monthly publications
- 🤖 Get AI-powered suggestions to improve content quality
- 👁️ Preview submissions in final rendered format
- 📋 Track submission status (Draft, Submitted, Approved, Rejected)
- 💾 Save drafts and submit later

### For Approvers
- 📥 Review submitted spotlights in a queue
- ✏️ Edit submissions with AI assistance
- ✅ Approve or reject submissions with feedback
- 🚀 Publish approved spotlights and send via email
- 📊 View publication statistics and history

### Technical Features
- 🔐 Authentication with role-based access control
- 🗄️ SQLite database for data persistence
- 🤖 AWS Bedrock integration for AI content enhancement
- 📧 Office 365 SMTP email integration
- 📱 Responsive web interface
- 🎨 Beautiful HTML email templates

## Installation

### Prerequisites
- Python 3.8 or higher
- AWS account with Bedrock access (for AI features)
- Office 365 email account (for email sending)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd organizational-spotlight-app
   ```

2. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your credentials
   # Use your preferred text editor
   ```

   Required environment variables:
   - `AWS_REGION`: Your AWS region (e.g., us-east-1)
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `SMTP_SERVER`: SMTP server (smtp.office365.com for Office 365)
   - `SMTP_PORT`: SMTP port (587 for Office 365)
   - `SMTP_EMAIL`: Your email address
   - `SMTP_PASSWORD`: Your email password or app password

5. **Initialize the database**
   ```bash
   python -m database.init_db
   ```

   This will:
   - Create the SQLite database
   - Generate 24 publication cycles for current year
   - Create sample user accounts

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The application will open in your default browser at `http://localhost:8501`

## Default User Accounts

The application comes with three demo accounts:

### User Accounts
- **Username:** user1
- **Password:** password123
- **Role:** User (can submit spotlights)

- **Username:** user2
- **Password:** password123
- **Role:** User (can submit spotlights)

### Approver Account
- **Username:** approver1
- **Password:** password123
- **Role:** Approver (can review and publish)

**⚠️ Important:** Change these credentials in production or use OAuth/SSO integration.

## Configuration

### Form Fields
Customize the submission form fields in `config/settings.py`:

```python
FORM_FIELDS = [
    {
        'name': 'title',
        'label': 'Spotlight Title',
        'type': 'text',
        'required': True,
        # ... more configuration
    },
    # Add more fields as needed
]
```

### Email Recipients
Configure default email recipients in `config/settings.py`:

```python
EMAIL_RECIPIENTS = [
    'all-staff@organization.com',
    'leadership@organization.com',
]
```

### Project Names
Customize available project names in `config/settings.py`:

```python
PROJECT_NAMES = [
    'Project Alpha',
    'Project Beta',
    # Add your projects
]
```

## User Guide

### For Users

#### Submitting a Spotlight

1. **Login** with your user credentials
2. **Select "New Submission"** from the sidebar
3. **Choose or enter a project name**
4. **Fill in the submission form** (required fields marked with *)
5. **Optional: Get AI Suggestions**
   - Click "Get AI Suggestions" button
   - Review the AI-enhanced version
   - Accept or reject the suggestions
6. **Preview your submission** to see how it will appear
7. **Submit** or save as draft

#### Viewing Your Submissions

1. Click **"My Submissions"** in the sidebar
2. Filter by status (Draft, Submitted, Approved, Rejected)
3. View details and status of each submission

### For Approvers

#### Reviewing Submissions

1. **Login** with your approver credentials
2. **Select "Review Queue"** from the sidebar
3. **Choose a publication** with pending submissions
4. **Review each submission:**
   - Read the content
   - Edit if needed
   - Get AI suggestions for improvements
   - Preview the final appearance
5. **Approve or Reject** the submission

#### Publishing Spotlights

1. **Select "Publish"** from the sidebar
2. **Choose a publication** with approved submissions
3. **Review all approved spotlights**
4. **Configure email recipients** (or use defaults)
5. **Preview the email** to verify formatting
6. **Click "Publish & Send"** to:
   - Mark publication as published
   - Send email to all recipients
   - Lock the publication

## Publication Cycles

The application automatically generates 24 publication cycles per year:
- **First Half:** 1st-15th of each month
- **Second Half:** 16th-end of each month

Publications are auto-generated for:
- Current year
- Next year (for advance planning)

## AWS Bedrock Integration

### Setup

1. **Enable AWS Bedrock** in your AWS account
2. **Request access** to Claude models (Anthropic)
3. **Create IAM credentials** with Bedrock permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
4. **Add credentials** to your .env file

### AI Enhancement

The AI service enhances submissions by:
- Improving clarity and readability
- Highlighting key achievements
- Using professional language
- Maintaining factual accuracy
- Keeping content concise

## Email Configuration

### Office 365 Setup

1. **Use app password** (recommended for MFA accounts):
   - Go to Office 365 security settings
   - Generate an app password
   - Use the app password in .env file

2. **SMTP Settings:**
   ```
   SMTP_SERVER=smtp.office365.com
   SMTP_PORT=587
   SMTP_EMAIL=your-email@organization.com
   SMTP_PASSWORD=your-app-password
   ```

### Email Template

The email template is located at `templates/email_template.html`. It features:
- Responsive design
- Outlook compatibility
- Professional styling
- Inline CSS for email client support

## Database Schema

### Tables
- **publications:** Publication cycles (24 per year)
- **submissions:** User submissions
- **submission_fields:** Dynamic field storage
- **ai_suggestions:** AI-generated suggestions
- **users:** User accounts

### Database Location
Default: `./database/spotlight.db`

Configure in .env: `DATABASE_PATH=./database/spotlight.db`

## Troubleshooting

### Database Issues

**Problem:** Database file not found
```bash
# Reinitialize database
python -m database.init_db
```

### AWS Bedrock Issues

**Problem:** Authentication failed
- Verify AWS credentials in .env
- Check IAM permissions
- Ensure Bedrock is enabled in your region

**Problem:** Model not found
- Request access to Claude models in AWS Console
- Wait for approval (may take 24-48 hours)

### Email Issues

**Problem:** Email not sending
- Verify SMTP credentials
- Check if 2FA requires app password
- Ensure port 587 is not blocked by firewall

**Problem:** Email formatting broken in Outlook
- Email template uses inline CSS for compatibility
- Test with Outlook desktop client
- Avoid complex layouts

### Authentication Issues

**Problem:** Login not working
- Verify users exist in database
- Check config/users.yaml
- Try default credentials (user1/password123)

## Development

### Project Structure
```
organizational-spotlight-app/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── config/
│   ├── settings.py          # Configuration
│   └── users.yaml           # User accounts
├── database/
│   ├── models.py            # Data models
│   ├── db_manager.py        # Database operations
│   └── init_db.py           # Initialization
├── auth/
│   ├── authenticator.py     # Authentication
│   └── oauth_handler.py     # OAuth (placeholder)
├── services/
│   ├── ai_service.py        # AWS Bedrock
│   ├── email_service.py     # Email sending
│   └── publication_service.py # Publication management
├── ui/
│   ├── components.py        # Reusable components
│   ├── user_dashboard.py    # User interface
│   └── approver_dashboard.py # Approver interface
├── templates/
│   ├── email_template.html  # Email template
│   └── preview_template.html # Preview template
└── utils/
    ├── validators.py        # Input validation
    └── helpers.py           # Helper functions
```

### Adding New Features

1. **Add new form fields:**
   - Edit `config/settings.py` → `FORM_FIELDS`
   - Fields are automatically rendered in UI

2. **Customize AI prompts:**
   - Edit `config/settings.py` → `AI_PROMPT_TEMPLATE`

3. **Modify email template:**
   - Edit `templates/email_template.html`
   - Use Jinja2 syntax for dynamic content

## Production Deployment

### Security Checklist
- [ ] Change all default passwords
- [ ] Use OAuth/SSO instead of local authentication
- [ ] Store secrets in secure vault (not .env)
- [ ] Enable HTTPS
- [ ] Restrict database file permissions
- [ ] Use environment-specific configurations
- [ ] Enable logging and monitoring
- [ ] Set up regular database backups

### Streamlit Cloud Deployment

1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy application

### Docker Deployment (Optional)

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review configuration settings
3. Check application logs
4. Contact your IT administrator

## License

Copyright © 2026 Your Organization. All rights reserved.

## Version History

### v1.0.0 (2026-02-19)
- Initial release
- User submission workflow
- Approver review workflow
- AI-powered content enhancement
- Email distribution
- Publication cycle management
