# Seeding — Generación e importación 🌱

**Resumen:** Cómo generar `documentum_seed.sql`/`documentum_seed_postgres.sql` a partir de Markdown y recomendaciones para producción.

## Generar desde Markdown (local)
```bash
python app/documentum/scripts/generate_documentum_sql.py --out documentum_seed.sql
python app/documentum/scripts/make_postgres_sql.py
```

## Importar en producción
- Sube `documentum_seed_postgres.sql` a la raíz del repo y ejecútalo via one‑off o:
```bash
python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render
```

## Notas
- `seed_documentum` es una alternativa que importa directamente desde Markdown si los archivos están en el servidor.
- El generador crea categorías basadas en la carpeta superior donde esté el MD (p.ej. `docs/operations/` -> categoría `operations`).
