# setup_db — Uso y flags 🔧

**Resumen:** Explicación del comando `setup_db` y cómo usarlo para restore, seed, normalize y render.

**Ejemplo principal:**

```bash
python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render
```

**Flags:**
- `--seed` — Ejecuta seed SQL.
- `--seed-sql <ruta>` — Ruta explícita al SQL.
- `--normalize` — Normaliza slugs.
- `--render` — Renderiza Markdown a HTML.
- `--force` — Forzar ejecución.

**Comportamiento:** el comando busca el SQL en varias ubicaciones (repo root, `app/documentum/sql/`, CWD) y es idempotente; si no encuentra SQL avisa y continúa (normalize+render).
