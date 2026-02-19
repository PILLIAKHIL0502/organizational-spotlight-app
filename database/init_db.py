"""
Database initialization script.
Creates tables and seeds initial data including 24 publication cycles per year.
"""

import os
from datetime import datetime
from database.db_manager import DatabaseManager


def generate_annual_publications(db_manager: DatabaseManager, year: int):
    """Generate all 24 publication cycles for a given year."""
    periods = ['first_half', 'second_half']

    for month in range(1, 13):  # 1-12
        for period in periods:
            try:
                pub = db_manager.create_publication(year, month, period)
                print(f"Created publication: {pub.get_display_name()}")
            except Exception as e:
                print(f"Publication already exists or error: {e}")


def seed_sample_users(db_manager: DatabaseManager):
    """Create sample users for testing."""
    sample_users = [
        ('user1@organization.com', 'John Doe', 'user'),
        ('user2@organization.com', 'Jane Smith', 'user'),
        ('approver1@organization.com', 'Admin User', 'approver'),
    ]

    for email, name, role in sample_users:
        try:
            user = db_manager.create_user(email, name, role)
            print(f"Created user: {user.name} ({user.role})")
        except Exception as e:
            print(f"User already exists or error: {e}")


def initialize_database(db_path: str = './database/spotlight.db'):
    """Initialize the database with tables and seed data."""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Initialize database manager
    db_manager = DatabaseManager(db_path)

    print("Creating database tables...")
    db_manager.create_tables()
    print("Tables created successfully!")

    # Generate publications for current year
    current_year = datetime.now().year
    print(f"\nGenerating publications for {current_year}...")
    generate_annual_publications(db_manager, current_year)

    # Optionally generate for next year as well
    print(f"\nGenerating publications for {current_year + 1}...")
    generate_annual_publications(db_manager, current_year + 1)

    # Seed sample users
    print("\nCreating sample users...")
    seed_sample_users(db_manager)

    print("\nDatabase initialization complete!")


if __name__ == '__main__':
    initialize_database()
