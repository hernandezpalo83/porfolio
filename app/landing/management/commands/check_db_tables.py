from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check if critical database tables exist (debugging for migrations)'

    def handle(self, *args, **options):
        tables_to_check = [
            'analytics_pageview',
            'analytics_sessiontracker',
            'analytics_postanalytics',
            'landing_menuitem',
            'auth_user',
        ]

        with connection.cursor() as cursor:
            # Get list of all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") if 'sqlite' in connection.settings_dict['ENGINE'] else cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            existing_tables = {row[0] for row in cursor.fetchall()}

        self.stdout.write(self.style.SUCCESS('Database Tables Status:'))
        self.stdout.write('-' * 50)

        for table in tables_to_check:
            status = '✓' if table in existing_tables else '✗'
            msg = f'{status} {table}'
            if table in existing_tables:
                self.stdout.write(self.style.SUCCESS(msg))
            else:
                self.stdout.write(self.style.ERROR(msg))
                logger.error(f"Missing table: {table}")

        self.stdout.write('-' * 50)
        self.stdout.write(f'Total tables found: {len(existing_tables)}')

        # If any critical tables are missing, exit with error
        critical_missing = [t for t in ['analytics_pageview', 'landing_menuitem'] if t not in existing_tables]
        if critical_missing:
            self.stdout.write(self.style.ERROR(f'\n⚠️ CRITICAL: Missing tables {critical_missing}. Run: python manage.py migrate'))
            exit(1)
