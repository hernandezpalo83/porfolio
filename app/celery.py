"""
Celery configuration for Django Portfolio project.

Celery is used for async tasks like batch saving PageViews to reduce DB latency.
Tasks are defined in app/tasks.py

Configuration:
- Broker: Redis (development: localhost:6379, production: CELERY_BROKER_URL env var)
- Result Backend: Redis
- Task routing: analytics tasks are eager in development
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.config.settings.development')

# Initialize Celery app
app = Celery('portfolio')

# Load config from Django settings with CELERY namespace
# All settings should use CELERY_ prefix in Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Beat Schedule: periodic tasks
# Example: Cleanup old PageViews weekly, aggregate analytics daily
app.conf.beat_schedule = {
    'cleanup-old-pageviews': {
        'task': 'app.tasks.cleanup_old_pageviews',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
