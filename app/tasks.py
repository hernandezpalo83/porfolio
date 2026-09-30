"""
Celery tasks for asynchronous operations.

Main uses:
- Batch saving PageViews to reduce N+1 query problem in analytics middleware
- Cleanup old tracking data
- Periodic aggregations
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db import IntegrityError

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def record_analytics_task(recorder: str, data: dict):
    """Record one anonymous page view or event (see app.analytics.middleware)."""
    from app.analytics import middleware
    from app.analytics.beacon import record_reading
    recorders = {'record_pageview': middleware.record_pageview, 'record_event_data': middleware.record_event_data,
                 'record_reading': record_reading}
    recorders[recorder](data)


@shared_task(bind=True, max_retries=3)
def batch_save_pageviews(self, pageviews_data: list):
    """
    Batch save multiple PageView records in a single operation.

    This reduces the latency impact of analytics middleware by batching
    multiple pageviews into one bulk_create call instead of CREATE per request.

    Args:
        pageviews_data (list): List of dicts with PageView fields

    Example:
        >> batch_save_pageviews.delay([
        >>     {'path': '/blog/', 'session_id': 'abc123', ...},
        >>     {'path': '/blog/post/', 'session_id': 'abc123', ...},
        >> ])

    Returns:
        dict: Result with count of created records
    """
    from app.analytics.models import PageView

    if not pageviews_data:
        return {'created': 0, 'batch_size': 0}

    try:
        # Create PageView instances from the batch data
        pageviews = [PageView(**data) for data in pageviews_data]

        # Bulk insert with ignore_conflicts to handle race conditions
        created = PageView.objects.bulk_create(pageviews, ignore_conflicts=True)

        logger.info(
            f"Batch saved {len(created)} PageViews. "
            f"Batch size: {len(pageviews_data)}, "
            f"Ignored conflicts: {len(pageviews_data) - len(created)}"
        )

        return {
            'created': len(created),
            'batch_size': len(pageviews_data),
            'conflicts_ignored': len(pageviews_data) - len(created),
        }

    except IntegrityError as e:
        # Retry on integrity errors (e.g., concurrent inserts)
        logger.warning(f"IntegrityError in batch_save_pageviews: {e}")
        raise self.retry(exc=e, countdown=5, backoff=2)
    except Exception as e:
        logger.error(f"Error in batch_save_pageviews: {e}", exc_info=True)
        # Don't retry for other errors, log and return failure
        return {'created': 0, 'error': str(e)}


@shared_task
def batch_save_sessions(sessions_data: list):
    """
    Batch save or update multiple SessionTracker records.

    Args:
        sessions_data (list): List of dicts with SessionTracker fields

    Returns:
        dict: Result with count of created/updated records
    """
    from app.analytics.models import SessionTracker

    if not sessions_data:
        return {'processed': 0}

    try:
        processed = 0
        for data in sessions_data:
            session_id = data.pop('session_id')
            SessionTracker.objects.update_or_create(
                session_id=session_id,
                defaults=data
            )
            processed += 1

        logger.info(f"Batch processed {processed} SessionTracker records")
        return {'processed': processed}

    except Exception as e:
        logger.error(f"Error in batch_save_sessions: {e}", exc_info=True)
        return {'processed': 0, 'error': str(e)}


@shared_task
def cleanup_old_pageviews(days: int = 90):
    """
    Delete PageView records older than N days.

    Runs daily via Celery Beat to keep the analytics table manageable.

    Args:
        days (int): Number of days to keep. Default: 90 days (3 months)

    Returns:
        dict: Result with count of deleted records
    """
    from app.analytics.models import PageView

    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = PageView.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()

        logger.info(f"Cleanup: deleted {deleted_count} old PageViews (>{days} days)")
        return {'deleted': deleted_count, 'days_threshold': days}

    except Exception as e:
        logger.error(f"Error in cleanup_old_pageviews: {e}", exc_info=True)
        return {'deleted': 0, 'error': str(e)}


@shared_task
def cleanup_old_sessions(days: int = 30):
    """
    Delete SessionTracker records older than N days.

    Args:
        days (int): Number of days to keep. Default: 30 days

    Returns:
        dict: Result with count of deleted records
    """
    from app.analytics.models import SessionTracker

    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = SessionTracker.objects.filter(
            updated_at__lt=cutoff_date
        ).delete()

        logger.info(f"Cleanup: deleted {deleted_count} old SessionTrackers (>{days} days)")
        return {'deleted': deleted_count, 'days_threshold': days}

    except Exception as e:
        logger.error(f"Error in cleanup_old_sessions: {e}", exc_info=True)
        return {'deleted': 0, 'error': str(e)}
