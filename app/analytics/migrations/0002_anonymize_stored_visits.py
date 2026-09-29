"""Remove the IP addresses and user-agents stored before analytics became anonymous."""
from django.db import migrations


def anonymize(apps, schema_editor):
    PageView = apps.get_model('analytics', 'PageView')
    PageView.objects.exclude(ip_address__isnull=True, user_agent__isnull=True).update(
        ip_address=None, user_agent=None
    )


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(anonymize, migrations.RunPython.noop),
    ]
