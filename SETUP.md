# Quick Setup Guide

Follow these steps to get the Organizational Spotlight application running quickly.

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.8 or higher installed
- [ ] AWS account with Bedrock access
- [ ] Office 365 email account
- [ ] Text editor for editing .env file

## Quick Start (5 minutes)

### 1. Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (2 min)

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# AWS Bedrock (required for AI features)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here

# Email (required for publishing)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_EMAIL=your-email@company.com
SMTP_PASSWORD=your_password_or_app_password
```

### 3. Initialize Database (1 min)
```bash
python -m database.init_db
```

You should see output like:
```
Creating database tables...
Tables created successfully!
Generating publications for 2026...
Created publication: First Half January 2026
...
```

### 4. Run Application (1 min)
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## First Login

Use these demo credentials:

**User Account:**
- Username: `user1`
- Password: `password123`

**Approver Account:**
- Username: `approver1`
- Password: `password123`

## Verify Setup

### Test User Features:
1. Login as user1
2. Click "New Submission"
3. Fill in a test submission
4. Click "Get AI Suggestions" (requires AWS setup)
5. Preview and submit

### Test Approver Features:
1. Logout and login as approver1
2. Click "Review Queue"
3. Review the test submission
4. Approve it
5. Go to "Publish" and preview the email

## Troubleshooting

### Database Error
```bash
# Delete and recreate database
rm database/spotlight.db
python -m database.init_db
```

### AWS Bedrock Not Working
- Option 1: Skip AI features (still fully functional)
- Option 2: Request Bedrock access in AWS Console
- Option 3: Use mock suggestions (set in code)

### Email Not Sending
- Use test mode: Don't click "Publish & Send"
- Just preview the email to verify formatting
- Configure SMTP later for actual sending

## Next Steps

1. **Customize Form Fields**
   - Edit `config/settings.py`
   - Modify `FORM_FIELDS` array
   - Restart application

2. **Add Real Users**
   - Edit `config/users.yaml`
   - Add usernames and hashed passwords
   - Or implement OAuth (see README.md)

3. **Configure Email Recipients**
   - Edit `config/settings.py`
   - Modify `EMAIL_RECIPIENTS` list

4. **Customize Email Template**
   - Edit `templates/email_template.html`
   - Test with "Preview Email" feature

## Production Checklist

Before deploying to production:
- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY in .env
- [ ] Use app passwords for email (if using MFA)
- [ ] Test email sending thoroughly
- [ ] Backup database regularly
- [ ] Set up monitoring/logging
- [ ] Use HTTPS
- [ ] Consider OAuth/SSO for authentication

## Getting Help

1. Check README.md for detailed documentation
2. Review configuration in `config/settings.py`
3. Check logs in terminal where app is running
4. Verify .env file has correct credentials

## Common Issues

**"Module not found" error:**
```bash
pip install -r requirements.txt --upgrade
```

**"Database is locked" error:**
```bash
# Make sure only one instance is running
# Restart the application
```

**"Authentication failed" error:**
- Check AWS credentials in .env
- Verify SMTP credentials in .env
- Ensure passwords don't have special characters that need escaping

**Streamlit won't start:**
```bash
# Try specifying port explicitly
streamlit run app.py --server.port 8501
```

## Success!

If you can see the login page and login with user1/password123, you're all set!

Enjoy using the Organizational Spotlight application! 🎉
