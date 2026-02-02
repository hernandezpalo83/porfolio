# Troubleshooting — Errores frecuentes y soluciones 🛠️

**Resumen:** Recopilación de problemas conocidos y fixes aplicables rápidamente.

- `NoReverseMatch: 'wiki' is not a registered namespace`: Añadir `path('wiki/', include('app.documentum.urls', namespace='wiki'))` a `app/config/urls.py`.
- `No se encontró archivo SQL de seed; saltando paso de seed.`: Asegúrate que `documentum_seed_postgres.sql` está en la rama desplegada.
- `Error ejecutando SQL: You can only execute one statement at a time.`: Solución: `setup_db` ahora usa `executescript` en SQLite y divide sentencias en otros DBs.
- `No module named 'markdown'`: Añadir `markdown` a `requirements.txt` y redeploy.

Si hay un nuevo stacktrace, pégalo aquí y lo investigamos.