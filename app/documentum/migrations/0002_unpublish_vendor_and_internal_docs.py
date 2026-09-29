"""
Take out of the public wiki the files that were imported by mistake: vendor
LICENSE/README files and internal project docs (CHANGELOG, PRODUCT.md).
They become drafts (still editable in the admin) and their URLs return 404.
"""
from django.db import migrations
from django.db.models import Q

UNPUBLISH = (
    Q(slug__startswith='license')
    | Q(slug__startswith='information-about-icons')
    | Q(title__iexact='CHANGELOG')
    | Q(title__iexact='PRODUCT.md')
)


def unpublish(apps, schema_editor):
    Document = apps.get_model('documentum', 'Document')
    Category = apps.get_model('documentum', 'Category')
    Document.objects.filter(UNPUBLISH, status='published').update(status='draft')
    for category in Category.objects.filter(is_visible=True):
        if not Document.objects.filter(category=category, status='published').exists():
            category.is_visible = False
            category.save(update_fields=['is_visible'])


class Migration(migrations.Migration):

    dependencies = [
        ('documentum', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(unpublish, migrations.RunPython.noop),
    ]
