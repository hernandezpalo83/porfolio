# Contribuir al proyecto

Gracias por contribuir. Sigue estas reglas para garantizar calidad y desplegabilidad.

1. Crea una rama clara: `feature/<descriptivo>` o `chore/<tema>`.
2. Añade tests para cambios funcionales y ejecuta `python manage.py test`.
3. Ejecuta pre-commit hooks y `python manage.py verify_urls` antes de commitear.
4. Documenta los cambios en `/docs/` y actualiza `README.md` si aplica.
5. Abre un PR con descripción clara, pasos para revisar y un ejemplo de comandos para reproducir.

Si el PR incluye cambios de infra / despliegue (p.ej. añadir `documentum_seed_postgres.sql`), añade instrucciones de verificación en `docs/deployment.md`.