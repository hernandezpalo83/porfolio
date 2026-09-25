from django.test import TestCase
from django.apps import apps
from unittest.mock import patch
import types

from app.documentum.models import Category, Document


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
        call_command('seed_documentum')
        docs = Document.objects.all()
        # Después de consolidación (2026-09-25), buscamos documentos en docs/ folder
        # Verifica que al menos existen documentos de arquitectura y componentes
        titles = set(d.title.lower() for d in docs)
        self.assertTrue(
            any('arquitect' in t for t in titles) or
            any('claude' in t for t in titles) or
            len(docs) > 5  # Al menos 5+ documentos importados
        )



class SetupDbLockTest(TestCase):
    def test_setup_db_advisory_lock_on_sqlite_returns_true(self):
        from app.landing.management.commands.setup_db import Command
        cmd = Command()
        self.assertTrue(cmd._acquire_lock())
