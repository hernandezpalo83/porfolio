# Arquitectura del Proyecto

Resumen rápido de la arquitectura y responsabilidades principales.

- Django (monorepo): varias apps responsables de partes separadas de la web.
  - `app.landing`: landing, navegación y páginas públicas.
  - `app.documentum`: documentación pública (ahora en `/wiki/`).
  - `app.blog`: entradas de blog.
  - `app.gym`: módulo de productos.

- Base de datos: PostgreSQL en producción (Supabase); tests locales usan SQLite.
- Backups: `db_backup.json` usado por `setup_db` para restauración inicial si la BD está vacía.
- Seeds: `documentum_seed_postgres.sql` (en repo cuando se necesita poblar documentum en prod).
- Sitemaps: claves `wiki_docs` y `wiki_cats` registradas para `documentum`.

Para detalles operativos consulta `docs/deployment.md` y `docs/setup_db.md`.