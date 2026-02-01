from django.test import TestCase
from django.core.management import call_command
from django.apps import apps
import tempfile
from pathlib import Path


class SetupDbCommandTests(TestCase):
    def setUp(self):
        self.Category = apps.get_model('documentum', 'Category')

    def _write_sql(self, sql_text):
        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql')
        tf.write(sql_text)
        tf.flush()
        tf.close()
        return tf.name

    def test_seed_executes_and_creates_category(self):
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Test Cat', 'test-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            # Ensure no categories initially
            self.assertEqual(self.Category.objects.count(), 0)
            call_command('setup_db', '--seed', '--seed-sql', path)
            self.assertTrue(self.Category.objects.filter(slug='test-cat').exists())
        finally:
            Path(path).unlink(missing_ok=True)

    def test_seed_skipped_when_category_exists_unless_force(self):
        self.Category.objects.create(name='Existing', slug='existing')
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('New Cat', 'new-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            call_command('setup_db', '--seed', '--seed-sql', path)
            # Since category existed, seed should be skipped and new-cat shouldn't exist
            self.assertFalse(self.Category.objects.filter(slug='new-cat').exists())

            # Now force
            call_command('setup_db', '--seed', '--seed-sql', path, '--force')
            self.assertTrue(self.Category.objects.filter(slug='new-cat').exists())
        finally:
            Path(path).unlink(missing_ok=True)
