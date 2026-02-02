# Troubleshooting — Errores frecuentes

Aquí se listan problemas que ya han ocurrido en este proyecto y cómo resolverlos.

- `NoReverseMatch: 'wiki' is not a registered namespace`:
  - Causa: cambios en templates al namespace `wiki` pero `app/config/urls.py` no lo registró.
  - Solución: registrar `path('wiki/', include('app.documentum.urls', namespace='wiki'))` y reintentar.

- `No se encontró archivo SQL de seed; saltando paso de seed.`:
  - Causa: `documentum_seed_postgres.sql` no está en el despliegue o no fue incluido en la rama desplegada.
  - Solución: añadir el archivo al repo y hacer deploy / ejecutar `setup_db --seed --seed-sql <ruta>`.

- `Error ejecutando SQL: You can only execute one statement at a time.`
  - Causa: SQL multi‑sentencia ejecutada con `cursor.execute` en SQLite.
  - Solución: `setup_db` ahora usa `executescript` para SQLite o divide sentencias para otros DBs.

- `No module named 'markdown'`:
  - Solución: `pip install -r requirements.txt` o añadir `markdown` a `requirements.txt` y redeploy.

- 500 en `/docs/...` por colisión con carpeta estática `/docs/`:
  - Solución aplicada: mover endpoint público a `/wiki/` para evitar la colisión estática.

Si encuentras algo nuevo, copia el stacktrace y abre un issue/PR con la reproducción y logs.