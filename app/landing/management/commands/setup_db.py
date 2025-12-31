import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
    help = "Inicializa la base de datos desde db_backup.json si está vacía"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando verificación de base de datos...")

        # Verificar si hay datos en cualquier modelo de landing o gym
        has_data = False
        for app_label in ["landing", "gym"]:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"La app '{app_label}' no está instalada"))
                continue

            for model in app_config.get_models():
                if model.objects.exists():
                    has_data = True
                    break
            if has_data:
                break

        if has_data:
            self.stdout.write(self.style.SUCCESS(
                "La base de datos ya contiene datos. No se restaura el backup."
            ))
            return

        # Posibles rutas donde buscar el backup
        posibles_rutas = [
            os.path.join(settings.BASE_DIR, "db_backup.json"),
            os.path.join(settings.BASE_DIR, "app", "db_backup.json"),
            os.path.join(settings.BASE_DIR, "app", "landing", "db_backup.json"),
        ]

        backup_file = None
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                backup_file = ruta
                break

        if not backup_file:
            self.stdout.write(self.style.WARNING(
                f"No se encontró db_backup.json en ninguna de las rutas: {posibles_rutas}. No se restaura nada."
            ))
            return

        self.stdout.write(self.style.WARNING(
            f"Base de datos vacía detectada. Restaurando desde {backup_file}..."
        ))

        try:
            call_command("loaddata", backup_file)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al restaurar el backup: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Base de datos restaurada correctamente."))
