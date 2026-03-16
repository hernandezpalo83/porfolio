from django.test import TransactionTestCase
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from pathlib import Path
import os
import tempfile


class SetupDbTests(TransactionTestCase):
    def setUp(self):
        self.Category = apps.get_model('documentum', 'Category')
        # Ensure categories are cleared before each test for true isolation (TransactionalTestCase does this, but doesn't hurt)
        self.Category.objects.all().delete()

    def _write_sql(self, sql_text):
        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql')
        tf.write(sql_text)
        tf.flush()
        tf.close()
        return tf.name

    def test_seed_executes_and_creates_category(self):
        """Verify that --seed executes provided SQL and creates data."""
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Test Cat', 'test-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            self.assertEqual(self.Category.objects.count(), 0)
            call_command('setup_db', '--seed', '--seed-sql', path)
            self.assertTrue(self.Category.objects.filter(slug='test-cat').exists())
        finally:
            Path(path).unlink(missing_ok=True)

    def test_seed_skipped_when_category_exists_unless_force(self):
        """Verify that seeding is skipped if data already exists, unless --force is used."""
        self.Category.objects.create(name='Existing', slug='existing')
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('New Cat', 'new-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            # Should skip because 'Existing' category exists
            call_command('setup_db', '--seed', '--seed-sql', path)
            self.assertFalse(self.Category.objects.filter(slug='new-cat').exists())

            # Should run because of --force
            call_command('setup_db', '--seed', '--seed-sql', path, '--force')
            self.assertTrue(self.Category.objects.filter(slug='new-cat').exists())
        finally:
            Path(path).unlink(missing_ok=True)

    def test_setup_db_finds_and_executes_default_candidate(self):
        """Verify that setup_db finds the default seed file in repo root (priority)."""
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Default Cat', 'default-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        # Highest priority candidate path
        full_path = Path(settings.BASE_DIR).parent / 'documentum_seed_postgres.sql'
        try:
            full_path.write_text(sql)
            # Slug must be unique, ensure it doesn't exist
            self.Category.objects.filter(slug='default-cat').delete()
            self.assertFalse(self.Category.objects.filter(slug='default-cat').exists())
            
            call_command('setup_db', '--seed-only')
            self.assertTrue(self.Category.objects.filter(slug='default-cat').exists())
        finally:
            if full_path.exists():
                full_path.unlink()


    def test_acquire_lock_returns_true_on_sqlite(self):
        """Postgres advisory locks should be skipped/mocked on SQLite."""
        from app.landing.management.commands.setup_db import Command
        cmd = Command()
        self.assertTrue(cmd._acquire_lock())
