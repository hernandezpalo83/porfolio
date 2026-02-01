from django.test import TestCase
from django.core.management import call_command
from django.apps import apps
from pathlib import Path
from django.conf import settings


class SetupDbRootCandidateTests(TestCase):
    def setUp(self):
        self.Category = apps.get_model('documentum', 'Category')

    def test_setup_db_finds_candidate_in_repo_root(self):
        # Create a candidate in repo root (BASE_DIR.parent)
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Root Cat', 'root-cat', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        root_path = Path(settings.BASE_DIR).parent / 'documentum_seed_postgres.sql'
        root_path.write_text(sql)
        try:
            self.assertFalse(self.Category.objects.filter(slug='root-cat').exists())
            call_command('setup_db', '--seed-only')
            self.assertTrue(self.Category.objects.filter(slug='root-cat').exists())
        finally:
            try:
                root_path.unlink()
            except Exception:
                pass
