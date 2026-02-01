from django.test import TestCase
from django.apps import apps
from unittest.mock import patch
import types
from pathlib import Path

from app.documentum.models import Category, Document, DocumentVersion


class DocumentumModelsTest(TestCase):
    def test_app_registered(self):
        """La app 'documentum' debe estar registrada en apps"""
        labels = [c.label for c in apps.get_app_configs()]
        self.assertIn('documentum', labels)

    def test_create_category_document_and_version(self):
        """Crear Category y Document debe generar una DocumentVersion automáticamente"""
        category = Category.objects.create(name='Infra', slug='infra')
        self.assertIsNotNone(category.pk)

        # Patch the markdown renderer module to avoid requiring the 'markdown' package in tests
        fake_utils = types.SimpleNamespace(render_markdown=lambda x: '<p>ok</p>')
        with patch.dict('sys.modules', {'app.documentum.utils': fake_utils}):
            document = Document.objects.create(
                title='Test Doc',
                slug='test-doc',
                category=category,
                content_markdown='Contenido de prueba',
                meta_description='Descripción de prueba',
            )

        self.assertIsNotNone(document.pk)

        # on save, Document should create a DocumentVersion
        versions = document.versions.all()
        self.assertEqual(versions.count(), 1)
        version = versions.first()
        self.assertEqual(version.content_markdown, 'Contenido de prueba')
        self.assertIsNotNone(version.pk)

    def test_seed_command_imports_markdown(self):
        """El comando seed_documentum debe importar los archivos Markdown del repo"""
        from django.core.management import call_command
        # Run the seeder
        call_command('seed_documentum')
        # There should be documents for at least DOCUMENTACION.md and CHANGELOG.md
        slugs = set(Document.objects.values_list('slug', flat=True))
        # flexible checks: Documento de documentación y changelog deben existir
        self.assertTrue(any('documentacion' in s for s in slugs) or Document.objects.filter(title__icontains='DOCUMENTACIÓN').exists())
        self.assertTrue(any('changelog' in s for s in slugs) or Document.objects.filter(title__icontains='CHANGELOG').exists())


class SetupDbIntegrationTest(TestCase):
    def _write_sql(self, sql_text):
        import tempfile
        tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql')
        tf.write(sql_text)
        tf.flush()
        tf.close()
        return tf.name

    def test_setup_db_executes_seed_sql(self):
        from django.core.management import call_command
        Category = apps.get_model('documentum', 'Category')
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('Test Cat 2', 'test-cat-2', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            self.assertEqual(Category.objects.count(), 0)
            call_command('setup_db', '--seed', '--seed-sql', path)
            self.assertTrue(Category.objects.filter(slug='test-cat-2').exists())
        finally:
            Path(path).unlink(missing_ok=True)

    def test_setup_db_skips_seed_unless_forced(self):
        from django.core.management import call_command
        Category = apps.get_model('documentum', 'Category')
        Category.objects.create(name='Existing', slug='existing')
        sql = """
        INSERT INTO documentum_category (name, slug, description, icon, "order", is_visible, created_at, updated_at) 
        VALUES ('New Cat 2', 'new-cat-2', 'desc', 'fa-book', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        """
        path = self._write_sql(sql)
        try:
            call_command('setup_db', '--seed', '--seed-sql', path)
            self.assertFalse(Category.objects.filter(slug='new-cat-2').exists())

            call_command('setup_db', '--seed', '--seed-sql', path, '--force')
            self.assertTrue(Category.objects.filter(slug='new-cat-2').exists())
        finally:
            Path(path).unlink(missing_ok=True)
