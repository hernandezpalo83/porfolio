from django.test import TestCase
from django.core.management import call_command
from django.apps import apps
from pathlib import Path
from django.conf import settings
import os


class SetupDbDefaultSeedTests(TestCase):
    def setUp(self):
        self.Category = apps.get_model('documentum', 'Category')

    def _write_default_candidate(self, name, sql_text):
        path = Path(settings.BASE_DIR) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sql_text)
        return str(path)

    def test_setup_db_skips_seed_when_provided_seed_sql_missing(self):
        # Provide a non-existing path explicitly; command should warn and skip, not raise
        missing = '/tmp/this_file_does_not_exist.sql'
        call_command('setup_db', '--seed', '--seed-sql', missing)
        # No exception: pass
        self.assertTrue(True)

    def test_setup_db_finds_and_executes_default_candidate(self):
        # Create a candidate at app/documentum/sql/documentum_seed_postgres.sql
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Default Cat', 'default-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        candidate_rel = Path('app') / 'documentum' / 'sql' / 'documentum_seed_postgres.sql'
        full_path = Path(settings.BASE_DIR) / candidate_rel
        full_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            full_path.write_text(sql)
            # Ensure no such category exists yet
            self.assertFalse(self.Category.objects.filter(slug='default-cat').exists())
            call_command('setup_db', '--seed-only')
            self.assertTrue(self.Category.objects.filter(slug='default-cat').exists())
        finally:
            try:
                full_path.unlink()
            except Exception:
                pass
