from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from app.documentum.models import Category, Document


class Command(BaseCommand):
    help = 'Normalize slugs for documentum Category and Document models to ASCII-only slugs and ensure uniqueness.'

    def handle(self, *args, **options):
        self.stdout.write('Normalizing Category slugs...')
        changed = 0
        with transaction.atomic():
            for cat in Category.objects.all():
                new_slug = slugify(cat.name, allow_unicode=False)
                if not new_slug:
                    new_slug = f'category-{cat.pk}'
                if new_slug != cat.slug:
                    orig = new_slug
                    counter = 1
                    while Category.objects.filter(slug=new_slug).exclude(pk=cat.pk).exists():
                        new_slug = f"{orig}-{counter}"
                        counter += 1
                    Category.objects.filter(pk=cat.pk).update(slug=new_slug)
                    self.stdout.write(f"Updated Category id={cat.pk} slug: '{cat.slug}' -> '{new_slug}'")
                    changed += 1
        self.stdout.write(f'Categories updated: {changed}')

        self.stdout.write('Normalizing Document slugs...')
        changed = 0
        with transaction.atomic():
            for doc in Document.objects.select_related('category').all():
                new_slug = slugify(doc.title, allow_unicode=False)
                if not new_slug:
                    new_slug = f'doc-{doc.pk}'
                # ensure global uniqueness (Document.slug is unique=True)
                orig = new_slug
                counter = 1
                while Document.objects.filter(slug=new_slug).exclude(pk=doc.pk).exists():
                    new_slug = f"{orig}-{counter}"
                    counter += 1
                if new_slug != doc.slug:
                    Document.objects.filter(pk=doc.pk).update(slug=new_slug)
                    self.stdout.write(f"Updated Document id={doc.pk} slug: '{doc.slug}' -> '{new_slug}'")
                    changed += 1
        self.stdout.write(f'Documents updated: {changed}')
        self.stdout.write(self.style.SUCCESS('Slug normalization complete.'))
