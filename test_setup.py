"""
Test script to verify setup and configuration.
Run this script to check if all components are properly configured.
"""

import sys
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")

    try:
        import streamlit
        print("✅ Streamlit installed")
    except ImportError:
        print("❌ Streamlit not installed. Run: pip install streamlit")
        return False

    try:
        import boto3
        print("✅ Boto3 installed")
    except ImportError:
        print("❌ Boto3 not installed. Run: pip install boto3")
        return False

    try:
        import yaml
        print("✅ PyYAML installed")
    except ImportError:
        print("❌ PyYAML not installed. Run: pip install pyyaml")
        return False

    try:
        import jinja2
        print("✅ Jinja2 installed")
    except ImportError:
        print("❌ Jinja2 not installed. Run: pip install jinja2")
        return False

    try:
        import streamlit_authenticator
        print("✅ Streamlit-authenticator installed")
    except ImportError:
        print("❌ Streamlit-authenticator not installed. Run: pip install streamlit-authenticator")
        return False

    return True


def test_project_structure():
    """Test if all required directories and files exist."""
    print("\nTesting project structure...")

    required_dirs = [
        'config', 'database', 'auth', 'services',
        'ui', 'templates', 'utils'
    ]

    required_files = [
        'app.py', 'requirements.txt', '.env.example',
        'config/settings.py', 'config/users.yaml',
        'database/models.py', 'database/db_manager.py',
        'auth/authenticator.py',
        'services/ai_service.py', 'services/email_service.py',
        'ui/components.py', 'ui/user_dashboard.py',
        'templates/email_template.html'
    ]

    all_good = True

    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            print(f"✅ Directory exists: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
            all_good = False

    for file_name in required_files:
        if Path(file_name).is_file():
            print(f"✅ File exists: {file_name}")
        else:
            print(f"❌ File missing: {file_name}")
            all_good = False

    return all_good


def test_configuration():
    """Test if configuration is properly set up."""
    print("\nTesting configuration...")

    # Check if .env exists
    if Path('.env').is_file():
        print("✅ .env file exists")

        # Check if it has required variables
        with open('.env', 'r') as f:
            content = f.read()

            required_vars = [
                'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
                'SMTP_SERVER', 'SMTP_PORT', 'SMTP_EMAIL', 'SMTP_PASSWORD'
            ]

            all_set = True
            for var in required_vars:
                if var in content and 'your_' not in content.split(var)[1].split('\n')[0]:
                    print(f"✅ {var} is configured")
                else:
                    print(f"⚠️  {var} needs to be configured in .env")
                    all_set = False

            return all_set
    else:
        print("❌ .env file not found. Copy .env.example to .env and configure it.")
        return False


def test_database():
    """Test if database can be initialized."""
    print("\nTesting database...")

    try:
        from database.db_manager import DatabaseManager
        from database.init_db import initialize_database

        # Test with temporary database
        test_db_path = 'test_spotlight.db'

        print("Initializing test database...")
        initialize_database(test_db_path)

        # Test basic operations
        db = DatabaseManager(test_db_path)

        # Test publication creation
        pub = db.create_publication(2026, 1, 'first_half')
        print(f"✅ Created test publication: {pub.get_display_name()}")

        # Test user creation
        user = db.create_user('test@test.com', 'Test User', 'user')
        print(f"✅ Created test user: {user.name}")

        # Clean up
        import os
        os.remove(test_db_path)
        print("✅ Database test successful")

        return True

    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False


def test_aws_bedrock():
    """Test AWS Bedrock connectivity (optional)."""
    print("\nTesting AWS Bedrock (optional)...")

    try:
        from services.ai_service import get_ai_service

        ai_service = get_ai_service()

        # Just test if we can initialize the client
        # Don't actually call the API
        print("⚠️  AWS Bedrock configured but not tested (to avoid API costs)")
        print("   The AI features will work if your AWS credentials are correct")

        return True

    except Exception as e:
        print(f"⚠️  AWS Bedrock test skipped: {str(e)}")
        print("   AI features will not work until AWS is configured")
        return True  # Not critical


def main():
    """Run all tests."""
    print("=" * 60)
    print("Organizational Spotlight - Setup Verification")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Configuration", test_configuration()))
    results.append(("Database", test_database()))
    results.append(("AWS Bedrock", test_aws_bedrock()))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("\nRun: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nRefer to README.md or SETUP.md for detailed instructions.")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
