"""
Publication service for managing publication cycles.
"""

from datetime import datetime
from typing import List, Optional
from database.db_manager import DatabaseManager
from database.models import Publication


class PublicationService:
    """Service for managing publication cycles."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the publication service.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def generate_annual_publications(self, year: int) -> List[Publication]:
        """
        Generate all 24 publication cycles for a given year (2 per month).

        Args:
            year: Year to generate publications for

        Returns:
            List of created Publication objects
        """
        publications = []
        periods = ['first_half', 'second_half']

        for month in range(1, 13):  # 1-12
            for period in periods:
                try:
                    pub = self.db.create_publication(year, month, period)
                    publications.append(pub)
                except Exception as e:
                    # Publication might already exist
                    print(f"Could not create publication for {year}-{month}-{period}: {e}")

        return publications

    def get_active_publication(self) -> Optional[Publication]:
        """
        Get the currently active (open) publication based on current date.

        Returns:
            Active Publication object or None if not found
        """
        return self.db.get_active_publication()

    def get_all_publications(self, year: Optional[int] = None) -> List[Publication]:
        """
        Get all publications, optionally filtered by year.

        Args:
            year: Optional year to filter by

        Returns:
            List of Publication objects
        """
        return self.db.get_all_publications(year)

    def get_publication_by_id(self, pub_id: int) -> Optional[Publication]:
        """
        Get a publication by its ID.

        Args:
            pub_id: Publication ID

        Returns:
            Publication object or None if not found
        """
        return self.db.get_publication(pub_id)

    def close_publication(self, pub_id: int) -> bool:
        """
        Close a publication and move it to 'under_review' status.

        Args:
            pub_id: Publication ID

        Returns:
            True if successful, False otherwise
        """
        return self.db.update_publication_status(pub_id, 'under_review')

    def publish_publication(self, pub_id: int) -> bool:
        """
        Finalize a publication and mark it as 'published'.

        Args:
            pub_id: Publication ID

        Returns:
            True if successful, False otherwise
        """
        return self.db.update_publication_status(pub_id, 'published')

    def get_publication_stats(self, pub_id: int) -> dict:
        """
        Get statistics for a publication.

        Args:
            pub_id: Publication ID

        Returns:
            Dictionary with publication statistics
        """
        submissions = self.db.get_submissions_by_publication(pub_id)

        stats = {
            'total': len(submissions),
            'draft': 0,
            'submitted': 0,
            'approved': 0,
            'rejected': 0
        }

        for sub in submissions:
            if sub.status in stats:
                stats[sub.status] += 1

        return stats

    def is_publication_ready_to_publish(self, pub_id: int) -> bool:
        """
        Check if a publication is ready to be published.
        A publication is ready if it has at least one approved submission
        and no pending submissions.

        Args:
            pub_id: Publication ID

        Returns:
            True if ready to publish, False otherwise
        """
        stats = self.get_publication_stats(pub_id)

        # Must have at least one approved submission
        if stats['approved'] == 0:
            return False

        # Should not have pending submissions (draft or submitted)
        if stats['draft'] > 0 or stats['submitted'] > 0:
            return False

        return True

    def get_upcoming_publications(self, limit: int = 5) -> List[Publication]:
        """
        Get upcoming open publications.

        Args:
            limit: Maximum number of publications to return

        Returns:
            List of upcoming Publication objects
        """
        now = datetime.now()
        all_pubs = self.db.get_all_publications()

        # Filter publications that are still open and in the future or current
        upcoming = []
        for pub in all_pubs:
            if pub.status == 'open':
                # Simple date comparison
                pub_date = datetime(pub.year, pub.month, 1)
                if pub_date >= datetime(now.year, now.month, 1):
                    upcoming.append(pub)

                if len(upcoming) >= limit:
                    break

        return upcoming

    def get_published_publications(self, year: Optional[int] = None,
                                   limit: Optional[int] = None) -> List[Publication]:
        """
        Get published publications.

        Args:
            year: Optional year to filter by
            limit: Optional limit on number of results

        Returns:
            List of published Publication objects
        """
        all_pubs = self.db.get_all_publications(year)

        published = [pub for pub in all_pubs if pub.status == 'published']

        if limit:
            published = published[:limit]

        return published

    def ensure_current_year_publications(self):
        """
        Ensure that publications exist for the current year.
        Creates them if they don't exist.
        """
        current_year = datetime.now().year

        # Check if any publications exist for current year
        current_year_pubs = self.db.get_all_publications(current_year)

        if not current_year_pubs:
            # Generate publications for current year
            self.generate_annual_publications(current_year)

    def get_period_date_range(self, year: int, month: int, period: str) -> tuple:
        """
        Get the date range for a publication period.

        Args:
            year: Year
            month: Month (1-12)
            period: 'first_half' or 'second_half'

        Returns:
            Tuple of (start_date, end_date) as datetime objects
        """
        if period == 'first_half':
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month, 15, 23, 59, 59)
        else:  # second_half
            start_date = datetime(year, month, 16)

            # Calculate last day of month
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)

            from datetime import timedelta
            end_date = next_month - timedelta(seconds=1)

        return start_date, end_date

    def is_publication_period_active(self, pub: Publication) -> bool:
        """
        Check if a publication period is currently active based on dates.

        Args:
            pub: Publication object

        Returns:
            True if the publication period is currently active
        """
        now = datetime.now()
        start_date, end_date = self.get_period_date_range(pub.year, pub.month, pub.period)

        return start_date <= now <= end_date
