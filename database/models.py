"""
Data models for the Organizational Spotlight application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Publication:
    """Represents a bi-monthly publication cycle."""
    id: Optional[int]
    year: int
    month: int
    period: str  # 'first_half' or 'second_half'
    status: str  # 'open', 'under_review', 'published'
    created_at: datetime
    published_at: Optional[datetime] = None

    def get_display_name(self) -> str:
        """Return a human-readable name for the publication."""
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        period_display = 'First Half' if self.period == 'first_half' else 'Second Half'
        return f"{period_display} {month_names[self.month - 1]} {self.year}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'period': self.period,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'display_name': self.get_display_name()
        }


@dataclass
class Submission:
    """Represents a user submission for a publication."""
    id: Optional[int]
    publication_id: int
    user_email: str
    project_name: str
    status: str  # 'draft', 'submitted', 'approved', 'rejected'
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'publication_id': self.publication_id,
            'user_email': self.user_email,
            'project_name': self.project_name,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


@dataclass
class SubmissionField:
    """Represents a field value in a submission."""
    id: Optional[int]
    submission_id: int
    field_name: str
    field_value: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class AISuggestion:
    """Represents AI-generated suggestions for a submission."""
    id: Optional[int]
    submission_id: int
    original_content: Dict[str, Any]
    suggested_content: Dict[str, Any]
    accepted: bool
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'original_content': self.original_content,
            'suggested_content': self.suggested_content,
            'accepted': self.accepted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class User:
    """Represents a user in the system."""
    email: str
    name: str
    role: str  # 'user' or 'approver'
    created_at: datetime
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
