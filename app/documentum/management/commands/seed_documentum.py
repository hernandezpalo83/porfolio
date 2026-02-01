from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from django.conf import settings

import sys
import types

from app.documentum.models import Category, Document

# Ensure a simple render_markdown exists if the markdown package isn't installed
try:
    import importlib
    importlib.import_module('app.documentum.utils')
except Exception:
    sys.modules['app.documentum.utils'] = types.SimpleNamespace(render_markdown=lambda x: x)


IGNORED_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}


def find_markdown_files(base_path: Path):
    for p in base_path.rglob('*.md'):
        # skip files in ignored directories
        if any(part in IGNORED_DIRS for part in p.parts):
            continue
        yield p


class Command(BaseCommand):
    help = 'Seed the documentum app with Markdown files found in the repository'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Folder to scan (defaults to project root)')
        parser.add_argument('--force', action='store_true', help='Force re-create documents (overwrite existing)')

    def handle(self, *args, **options):
        base = options.get('path')
        force = options.get('force')

        if base:
            base_path = Path(base)
        else:
            # try to find repository root by locating manage.py
            p = Path(__file__).resolve()
            matches = [parent for parent in p.parents if (parent / 'manage.py').exists()]
            repo_root = matches[-1] if matches else None  # prefer the outermost manage.py
            base_path = repo_root or Path(settings.BASE_DIR)

        self.stdout.write(self.style.NOTICE(f'Scanning for markdown files under: {base_path}'))

        files = list(find_markdown_files(base_path))
        if not files:
            self.stdout.write(self.style.WARNING('No Markdown files found.'))
            return

        created = 0
        skipped = 0

        with transaction.atomic():
            for md in sorted(files):
                rel = md.relative_to(base_path)
                parts = rel.parts
                category_name = parts[0] if len(parts) > 1 else 'General'
                category_slug = slugify(category_name)

                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': category_slug, 'description': f'Imported from {category_name}'}
                )

                raw = md.read_text(encoding='utf-8')
                # title: first line that starts with '#', otherwise filename stem
                title = None
                meta_description = ''
                for line in raw.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if not title and line.startswith('#'):
                        title = line.lstrip('#').strip()
                    if not meta_description and line:
                        meta_description = line[:160]
                        break
                if not title:
                    title = md.stem.replace('_', ' ').replace('-', ' ').title()

                slug = slugify(title)

                # check existing
                existing = Document.objects.filter(slug=slug, category=category).first()
                if existing and not force:
                    self.stdout.write(self.style.WARNING(f'Skipping existing document: {title}'))
                    skipped += 1
                    continue

                if existing and force:
                    existing.delete()

                doc = Document.objects.create(
                    title=title,
                    slug=slug,
                    category=category,
                    content_markdown=raw,
                    meta_description=meta_description or f'Imported from {md.name}',
                    status='published',
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created document: {title} (category: {category_name})'))

        self.stdout.write(self.style.SUCCESS(f'Done. Created: {created}, Skipped: {skipped}'))
