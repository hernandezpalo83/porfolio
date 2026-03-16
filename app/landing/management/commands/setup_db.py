import os
import tempfile
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.apps import apps
from django.db import connection, transaction


class Command(BaseCommand):
    help = (
        "Inicializa la base de datos desde db_backup.json si está vacía y opcionalmente ejecuta seed SQL, "
        "normaliza slugs y renderiza Markdown a HTML."
    )

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Forzar la ejecución incluso si la BD contiene datos')
        parser.add_argument('--seed', action='store_true', help='Ejecutar seed SQL para documentum (por defecto busca documentum_seed_postgres.sql en la raíz)')
        parser.add_argument('--seed-sql', dest='seed_sql', help='Ruta al archivo SQL de seed a ejecutar (si se omite usa documentum_seed_postgres.sql)')
        parser.add_argument('--normalize', action='store_true', help='Ejecutar normalize_documentum_slugs después del seed')
        parser.add_argument('--render', action='store_true', help='Ejecutar render_documentum_html después del seed')
        parser.add_argument('--seed-only', action='store_true', help='Solo ejecutar el seed y salir')
        parser.add_argument('--normalize-only', action='store_true', help='Solo ejecutar normalize_documentum_slugs y salir')
        parser.add_argument('--render-only', action='store_true', help='Solo ejecutar render_documentum_html y salir')

    def _db_has_data(self):
        for app_label in ["landing", "gym"]:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"La app '{app_label}' no está instalada"))
                continue

            for model in app_config.get_models():
                if model.objects.exists():
                    return True
        return False

    def _find_default_seed_sql(self):
        # BASE_DIR is .../porfolio/app
        # We want to check:
        # 1. BASE_DIR.parent (repo root)
        # 2. BASE_DIR / 'documentum' / 'sql' (app internal sql)
        repo_root = Path(settings.BASE_DIR).parent
        app_sql = Path(settings.BASE_DIR) / 'documentum' / 'sql'
        
        candidates = [
            repo_root / 'documentum_seed_postgres.sql',
            repo_root / 'documentum_seed.sql',
            app_sql / 'documentum_seed_postgres.sql',
            app_sql / 'documentum_seed.sql',
            # Fallbacks for BASE_DIR if it were pointing to root (flexible)
            Path(settings.BASE_DIR) / 'documentum_seed_postgres.sql',
            Path(settings.BASE_DIR) / 'documentum_seed.sql',
        ]
        seen = set()
        self.stdout.write('Buscando archivo SQL de seed en ubicaciones candidatas:')
        for p in candidates:
            # Avoid duplicate paths
            try:
                real = str(p.resolve())
            except Exception:
                real = str(p)
            if real in seen:
                continue
            seen.add(real)
            self.stdout.write(f'  - {p}')
            if p.exists():
                self.stdout.write(self.style.SUCCESS(f'Archivo SQL encontrado: {p}'))
                return str(p)
        self.stdout.write(self.style.WARNING('No se encontró archivo SQL de seed en ubicaciones candidatas.'))
        return None

    def _execute_sql_file(self, path):
        self.stdout.write(f"Ejecutando SQL desde {path}...")
        sql = Path(path).read_text()
        vendor = connection.vendor
        
        # SQLite specific fixes
        if vendor == 'sqlite':
            # Replace postgres-specific now() with SQLite CURRENT_TIMESTAMP
            import re
            sql = re.sub(r'\bnow\(\)', 'CURRENT_TIMESTAMP', sql)
            # Remove ON CONFLICT DO NOTHING (sqlite supports ON CONFLICT, but syntax varies)
            # For simplicity in seed, we just try to execute. 
            # SQLite supports ON CONFLICT since 3.24.0.
            
        try:
            with transaction.atomic():
                # SQLite: use the underlying connection's executescript for multi-statement files
                if vendor == 'sqlite':
                    raw = connection.connection
                    try:
                        raw.executescript(sql)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error ejecutando SQL (SQLite execscript): {e}"))
                        raise
                else:
                    # For other DBs (e.g., Postgres), execute statements one-by-one
                    statements = [s.strip() for s in sql.split(';') if s.strip()]
                    with connection.cursor() as cur:
                        for stmt in statements:
                            cur.execute(stmt)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error ejecutando SQL: {e}"))
            raise
        self.stdout.write(self.style.SUCCESS("SQL ejecutado correctamente."))

    def _acquire_lock(self, lock_id: int = 987654321) -> bool:
        """Try to acquire an advisory lock on Postgres. Returns True if lock acquired or running on non-Postgres."""
        vendor = connection.vendor
        if vendor != 'postgresql':
            # For SQLite and others assume single-process dev environment
            self.stdout.write('Non-Postgres DB detected; skipping advisory lock.')
            return True
        try:
            with connection.cursor() as cur:
                cur.execute('SELECT pg_try_advisory_lock(%s)', [lock_id])
                row = cur.fetchone()
                acquired = bool(row and row[0])
                if acquired:
                    self.stdout.write('Advisory lock acquired.')
                else:
                    self.stdout.write('Could not acquire advisory lock (another process may be running).')
                return acquired
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Advisory lock failed: {e}. Proceeding without lock."))
            return True

    def _release_lock(self, lock_id: int = 987654321) -> None:
        vendor = connection.vendor
        if vendor != 'postgresql':
            return
        try:
            with connection.cursor() as cur:
                cur.execute('SELECT pg_advisory_unlock(%s)', [lock_id])
                self.stdout.write('Advisory lock released.')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to release advisory lock: {e}"))

    def handle(self, *args, **options):
        force = options.get('force')
        do_seed = options.get('seed')
        seed_sql = options.get('seed_sql')
        do_normalize = options.get('normalize')
        do_render = options.get('render')
        seed_only = options.get('seed_only')
        normalize_only = options.get('normalize_only')
        render_only = options.get('render_only')

        # If any *-only flags are provided, they take precedence
        if seed_only:
            do_seed = True
            do_normalize = False
            do_render = False
        if normalize_only:
            do_normalize = True
            do_seed = False
            do_render = False
        if render_only:
            do_render = True
            do_seed = False
            do_normalize = False

        # If no explicit flags provided, assume we want to run all steps (seed, normalize, render)
        if not any([do_seed, do_normalize, do_render]):
            do_seed = True
            do_normalize = True
            do_render = True

        has_data = self._db_has_data()
        if has_data and not force:
            self.stdout.write(self.style.SUCCESS(
                "La base de datos contiene datos. Se ejecutarán tareas idempotentes (seed solo si falta contenido, normalize, render)."
            ))

        # If DB empty and no operation-only flags, try to restore from db_backup.json
        if not has_data and not any([seed_only, normalize_only, render_only]):
            self.stdout.write("Iniciando verificación de base de datos... (vacía)")

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

            if backup_file:
                self.stdout.write(self.style.WARNING(
                    f"Base de datos vacía detectada. Restaurando desde {backup_file}..."
                ))

                try:
                    call_command("loaddata", backup_file)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error al restaurar el backup: {e}"))
                    return

                self.stdout.write(self.style.SUCCESS("Base de datos restaurada correctamente."))
            else:
                self.stdout.write(self.style.WARNING(
                    f"No se encontró db_backup.json en ninguna de las rutas: {posibles_rutas}. No se restaura nada."
                ))

        # Acquire advisory lock (Postgres) to avoid concurrent runs
        got_lock = self._acquire_lock()
        if not got_lock:
            self.stdout.write(self.style.WARNING('No se obtuvo lock; asumiendo que otro proceso está realizando setup. Saliendo.'))
            return

        try:
            # SEED step
            if do_seed:
                # Resolve seed SQL path
                if not seed_sql:
                    seed_sql = self._find_default_seed_sql()

                # If a seed path was provided but doesn't exist, warn and skip seed
                if seed_sql and not Path(seed_sql).exists():
                    self.stdout.write(self.style.WARNING(f"Seed SQL proporcionado no existe: {seed_sql}. Saltando seed."))
                    should_run_seed = False
                elif not seed_sql:
                    # No seed file available: skip seed but continue with normalize/render
                    self.stdout.write(self.style.WARNING("No se encontró archivo SQL de seed; saltando paso de seed."))
                    should_run_seed = False

                # Determine whether to run seed: only when documentum is empty or if --force (unless already decided)
                try:
                    from app.documentum.models import Category
                except Exception:
                    Category = None

                if 'should_run_seed' not in locals():
                    should_run_seed = force
                    if not should_run_seed:
                        if Category is None:
                            # If model not available, try to run seed to create tables/data
                            should_run_seed = True
                        else:
                            should_run_seed = (Category.objects.count() == 0)
                try:
                    from app.documentum.models import Category
                except Exception:
                    Category = None

                should_run_seed = force
                if not should_run_seed:
                    if Category is None:
                        # If model not available, try to run seed to create tables/data
                        should_run_seed = True
                    else:
                        should_run_seed = (Category.objects.count() == 0)

                if should_run_seed:
                    try:
                        self._execute_sql_file(seed_sql)
                    except Exception:
                        self.stdout.write(self.style.ERROR("Seed SQL falló. Abortando."))
                        return
                else:
                    self.stdout.write(self.style.SUCCESS("Seed SQL omitido: ya existen categorías de documentum."))

                if seed_only:
                    return

            # NORMALIZE step
            if do_normalize:
                try:
                    self.stdout.write('Ejecutando normalize_documentum_slugs...')
                    call_command('normalize_documentum_slugs')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error en normalize_documentum_slugs: {e}"))
                    return
                if normalize_only:
                    return

            # RENDER step
            if do_render:
                try:
                    self.stdout.write('Ejecutando render_documentum_html...')
                    call_command('render_documentum_html', '--force')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error en render_documentum_html: {e}"))
                    return
                if render_only:
                    return

        finally:
            # Release the advisory lock if we acquired it
            try:
                self._release_lock()
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS('setup_db finalizado.'))
