import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from landing.models import Proyecto
from gym.models import Ejercicio


class Command(BaseCommand):
    help = "Inicializa la base de datos desde db_backup.json si está vacía"

    def handle(self, *args, **options):
        has_landing_data = Proyecto.objects.exists()
        has_gym_data = Ejercicio.objects.exists()

        if has_landing_data or has_gym_data:
            self.stdout.write(
                self.style.SUCCESS("La base de datos ya contiene datos. No se restaura el backup.")
            )
            return

        backup_file = os.path.join(settings.BASE_DIR, "db_backup.json")

        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.WARNING("No se encontró db_backup.json. No se restaura nada.")
            )
            return

        self.stdout.write("Base de datos vacía detectada. Restaurando desde db_backup.json...")
        call_command("loaddata", backup_file)
        self.stdout.write(
            self.style.SUCCESS("Base de datos restaurada correctamente.")
        )
