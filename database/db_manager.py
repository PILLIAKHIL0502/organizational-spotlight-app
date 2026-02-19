"""
Database manager for the Organizational Spotlight application.
Handles all database operations using SQLite.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from database.models import (
    Publication, Submission, SubmissionField, AISuggestion, User
)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_path: str):
        """Initialize the database manager."""
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_tables(self):
        """Create all database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Publications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TIMESTAMP NOT NULL,
                    published_at TIMESTAMP,
                    UNIQUE(year, month, period)
                )
            ''')

            # Submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    publication_id INTEGER NOT NULL,
                    user_email TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    submitted_at TIMESTAMP,
                    reviewed_by TEXT,
                    reviewed_at TIMESTAMP,
                    FOREIGN KEY (publication_id) REFERENCES publications(id)
                )
            ''')

            # Submission fields table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submission_fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    field_value TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (submission_id) REFERENCES submissions(id)
                )
            ''')

            # AI suggestions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    original_content TEXT NOT NULL,
                    suggested_content TEXT NOT NULL,
                    accepted INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (submission_id) REFERENCES submissions(id)
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP
                )
            ''')

    # Publication CRUD operations
    def create_publication(self, year: int, month: int, period: str) -> Publication:
        """Create a new publication."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_at = datetime.now()

            cursor.execute('''
                INSERT INTO publications (year, month, period, status, created_at)
                VALUES (?, ?, ?, 'open', ?)
            ''', (year, month, period, created_at))

            pub_id = cursor.lastrowid

            return Publication(
                id=pub_id,
                year=year,
                month=month,
                period=period,
                status='open',
                created_at=created_at
            )

    def get_publication(self, pub_id: int) -> Optional[Publication]:
        """Get a publication by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM publications WHERE id = ?', (pub_id,))
            row = cursor.fetchone()

            if row:
                return Publication(
                    id=row['id'],
                    year=row['year'],
                    month=row['month'],
                    period=row['period'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None
                )
            return None

    def get_all_publications(self, year: Optional[int] = None) -> List[Publication]:
        """Get all publications, optionally filtered by year."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if year:
                cursor.execute(
                    'SELECT * FROM publications WHERE year = ? ORDER BY year DESC, month DESC, period',
                    (year,)
                )
            else:
                cursor.execute('SELECT * FROM publications ORDER BY year DESC, month DESC, period')

            rows = cursor.fetchall()
            publications = []

            for row in rows:
                publications.append(Publication(
                    id=row['id'],
                    year=row['year'],
                    month=row['month'],
                    period=row['period'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None
                ))

            return publications

    def get_active_publication(self) -> Optional[Publication]:
        """Get the currently active (open) publication based on current date."""
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day

        period = 'first_half' if day <= 15 else 'second_half'

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM publications
                WHERE year = ? AND month = ? AND period = ? AND status = 'open'
            ''', (year, month, period))

            row = cursor.fetchone()

            if row:
                return Publication(
                    id=row['id'],
                    year=row['year'],
                    month=row['month'],
                    period=row['period'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None
                )
            return None

    def update_publication_status(self, pub_id: int, status: str) -> bool:
        """Update publication status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if status == 'published':
                cursor.execute('''
                    UPDATE publications
                    SET status = ?, published_at = ?
                    WHERE id = ?
                ''', (status, datetime.now(), pub_id))
            else:
                cursor.execute('''
                    UPDATE publications
                    SET status = ?
                    WHERE id = ?
                ''', (status, pub_id))

            return cursor.rowcount > 0

    # Submission CRUD operations
    def create_submission(self, publication_id: int, user_email: str,
                         project_name: str, fields: Dict[str, str]) -> Submission:
        """Create a new submission with fields."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()

            # Create submission
            cursor.execute('''
                INSERT INTO submissions
                (publication_id, user_email, project_name, status, created_at, updated_at)
                VALUES (?, ?, ?, 'draft', ?, ?)
            ''', (publication_id, user_email, project_name, now, now))

            submission_id = cursor.lastrowid

            # Create submission fields
            for field_name, field_value in fields.items():
                # Convert lists to comma-separated strings for SQLite storage
                if isinstance(field_value, list):
                    field_value = ', '.join(str(item) for item in field_value)

                cursor.execute('''
                    INSERT INTO submission_fields
                    (submission_id, field_name, field_value, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (submission_id, field_name, str(field_value), now))

            return Submission(
                id=submission_id,
                publication_id=publication_id,
                user_email=user_email,
                project_name=project_name,
                status='draft',
                created_at=now,
                updated_at=now
            )

    def get_submission(self, submission_id: int) -> Optional[Submission]:
        """Get a submission by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
            row = cursor.fetchone()

            if row:
                return Submission(
                    id=row['id'],
                    publication_id=row['publication_id'],
                    user_email=row['user_email'],
                    project_name=row['project_name'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    submitted_at=datetime.fromisoformat(row['submitted_at']) if row['submitted_at'] else None,
                    reviewed_by=row['reviewed_by'],
                    reviewed_at=datetime.fromisoformat(row['reviewed_at']) if row['reviewed_at'] else None
                )
            return None

    def get_submission_fields(self, submission_id: int) -> Dict[str, str]:
        """Get all fields for a submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT field_name, field_value
                FROM submission_fields
                WHERE submission_id = ?
            ''', (submission_id,))

            rows = cursor.fetchall()
            return {row['field_name']: row['field_value'] for row in rows}

    def get_submissions_by_publication(self, publication_id: int,
                                      status: Optional[str] = None) -> List[Submission]:
        """Get all submissions for a publication."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if status:
                cursor.execute('''
                    SELECT * FROM submissions
                    WHERE publication_id = ? AND status = ?
                    ORDER BY created_at DESC
                ''', (publication_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM submissions
                    WHERE publication_id = ?
                    ORDER BY created_at DESC
                ''', (publication_id,))

            rows = cursor.fetchall()
            submissions = []

            for row in rows:
                submissions.append(Submission(
                    id=row['id'],
                    publication_id=row['publication_id'],
                    user_email=row['user_email'],
                    project_name=row['project_name'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    submitted_at=datetime.fromisoformat(row['submitted_at']) if row['submitted_at'] else None,
                    reviewed_by=row['reviewed_by'],
                    reviewed_at=datetime.fromisoformat(row['reviewed_at']) if row['reviewed_at'] else None
                ))

            return submissions

    def get_submissions_by_user(self, user_email: str) -> List[Submission]:
        """Get all submissions by a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM submissions
                WHERE user_email = ?
                ORDER BY created_at DESC
            ''', (user_email,))

            rows = cursor.fetchall()
            submissions = []

            for row in rows:
                submissions.append(Submission(
                    id=row['id'],
                    publication_id=row['publication_id'],
                    user_email=row['user_email'],
                    project_name=row['project_name'],
                    status=row['status'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    submitted_at=datetime.fromisoformat(row['submitted_at']) if row['submitted_at'] else None,
                    reviewed_by=row['reviewed_by'],
                    reviewed_at=datetime.fromisoformat(row['reviewed_at']) if row['reviewed_at'] else None
                ))

            return submissions

    def update_submission_status(self, submission_id: int, status: str,
                                reviewed_by: Optional[str] = None) -> bool:
        """Update submission status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()

            if status == 'submitted':
                cursor.execute('''
                    UPDATE submissions
                    SET status = ?, submitted_at = ?, updated_at = ?
                    WHERE id = ?
                ''', (status, now, now, submission_id))
            elif status in ['approved', 'rejected']:
                cursor.execute('''
                    UPDATE submissions
                    SET status = ?, reviewed_by = ?, reviewed_at = ?, updated_at = ?
                    WHERE id = ?
                ''', (status, reviewed_by, now, now, submission_id))
            else:
                cursor.execute('''
                    UPDATE submissions
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                ''', (status, now, submission_id))

            return cursor.rowcount > 0

    def update_submission_fields(self, submission_id: int, fields: Dict[str, str]) -> bool:
        """Update submission fields."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()

            # Delete existing fields
            cursor.execute('DELETE FROM submission_fields WHERE submission_id = ?',
                          (submission_id,))

            # Insert updated fields
            for field_name, field_value in fields.items():
                # Convert lists to comma-separated strings for SQLite storage
                if isinstance(field_value, list):
                    field_value = ', '.join(str(item) for item in field_value)

                cursor.execute('''
                    INSERT INTO submission_fields
                    (submission_id, field_name, field_value, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (submission_id, field_name, str(field_value), now))

            # Update submission updated_at
            cursor.execute('''
                UPDATE submissions
                SET updated_at = ?
                WHERE id = ?
            ''', (now, submission_id))

            return True

    # AI Suggestions operations
    def save_ai_suggestion(self, submission_id: int, original_content: Dict[str, Any],
                          suggested_content: Dict[str, Any], accepted: bool = False) -> int:
        """Save AI suggestions for a submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute('''
                INSERT INTO ai_suggestions
                (submission_id, original_content, suggested_content, accepted, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (submission_id, json.dumps(original_content),
                  json.dumps(suggested_content), int(accepted), now))

            return cursor.lastrowid

    def get_ai_suggestions(self, submission_id: int) -> List[AISuggestion]:
        """Get all AI suggestions for a submission."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ai_suggestions
                WHERE submission_id = ?
                ORDER BY created_at DESC
            ''', (submission_id,))

            rows = cursor.fetchall()
            suggestions = []

            for row in rows:
                suggestions.append(AISuggestion(
                    id=row['id'],
                    submission_id=row['submission_id'],
                    original_content=json.loads(row['original_content']),
                    suggested_content=json.loads(row['suggested_content']),
                    accepted=bool(row['accepted']),
                    created_at=datetime.fromisoformat(row['created_at'])
                ))

            return suggestions

    def update_ai_suggestion_accepted(self, suggestion_id: int, accepted: bool) -> bool:
        """Update whether an AI suggestion was accepted."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE ai_suggestions
                SET accepted = ?
                WHERE id = ?
            ''', (int(accepted), suggestion_id))

            return cursor.rowcount > 0

    # User operations
    def create_user(self, email: str, name: str, role: str) -> User:
        """Create a new user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()

            cursor.execute('''
                INSERT INTO users (email, name, role, created_at)
                VALUES (?, ?, ?, ?)
            ''', (email, name, role, now))

            return User(
                email=email,
                name=name,
                role=role,
                created_at=now
            )

    def get_user(self, email: str) -> Optional[User]:
        """Get a user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()

            if row:
                return User(
                    email=row['email'],
                    name=row['name'],
                    role=row['role'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None
                )
            return None

    def update_user_last_login(self, email: str) -> bool:
        """Update user's last login timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET last_login = ?
                WHERE email = ?
            ''', (datetime.now(), email))

            return cursor.rowcount > 0
