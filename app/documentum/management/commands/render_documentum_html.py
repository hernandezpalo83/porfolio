from django.core.management.base import BaseCommand
from django.utils import timezone
from app.documentum.models import Document


class Command(BaseCommand):
    help = 'Render Markdown to HTML for documents and update content_html field. Use --force to re-render existing HTML.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Re-render content_html even if it exists')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without applying changes')

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        qs = Document.objects.all()
        if not force:
            qs = qs.filter(content_html='')

        total = qs.count()
        if total == 0:
            self.stdout.write('No documents to render.')
            return

        self.stdout.write(f'Found {total} documents to render (force={force}, dry_run={dry_run}).')

        from app.documentum.utils import render_markdown

        updated = 0
        for doc in qs.iterator():
            html = render_markdown(doc.content_markdown)
            if html != doc.content_html:
                self.stdout.write(f"Will update Document id={doc.id} slug='{doc.slug}' title='{doc.title}'")
                if not dry_run:
                    Document.objects.filter(pk=doc.pk).update(content_html=html, updated_at=timezone.now())
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} documents.'))
