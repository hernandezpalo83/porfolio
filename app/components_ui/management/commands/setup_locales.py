import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Create translation directories and makemessages'

    def handle(self, *args, **options):
        # We need to make sure the directories exist.
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        locales_dir = os.path.join(base_dir, 'locales')
        os.makedirs(os.path.join(locales_dir, 'es', 'LC_MESSAGES'), exist_ok=True)
        os.makedirs(os.path.join(locales_dir, 'en', 'LC_MESSAGES'), exist_ok=True)
        self.stdout.write(self.style.SUCCESS("Locales directory created."))
