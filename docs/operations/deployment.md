# Despliegue en Render 🚀

**Resumen:** Cómo desplegar el proyecto en Render y ejecutar la importación de la documentación (`/wiki/`).

**Verificación rápida:** Ejecuta `python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render` en un one‑off de Render y comprueba los logs.

## Pasos
1. Mergea a `main` y espera el deploy.
2. En Render: Web Service → More → Run One‑off Command.
3. Ejecuta:

```bash
python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render
```

## Notas
- Revisa `Updated X documents.` en los logs para confirmar que la importación y el render se realizaron.
- Si no encuentras `documentum_seed_postgres.sql` en los logs, confirma que está en la rama desplegada.
