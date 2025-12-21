# ✅ Checklist de Deploy en Render.com

## 📋 Fase 1: Preparación Local

- [ ] **Eliminar referencias a Fly.io**
  - [x] fly.toml eliminados
  - [x] Dockerfile actualizado para Render
  - [x] .gitignore actualizado

- [ ] **Crear archivos necesarios**
  - [x] render.yaml
  - [x] Dockerfile
  - [x] Scripts (deploy-render.sh, quickstart-render.sh)
  - [x] Inicializadores (migrate_to_render.py, init_render_db.py)
  - [x] Documentación (RENDER_DEPLOYMENT.md, QUICKSTART_RENDER.md)
  - [x] Variables de ejemplo (.env.example)

- [ ] **Exportar datos locales**
  ```bash
  ./deploy-render.sh export
  ```
  - [ ] datos_full.json creado
  - [ ] datos_full.json.gz creado (opcional)

- [ ] **Hacer commit de cambios**
  ```bash
  git add -A
  git commit -m "Migrar a Render.com - eliminar Fly.io"
  ```

## 🌐 Fase 2: Configuración en Render.com

- [ ] **Crear Web Service**
  - [ ] Ir a https://dashboard.render.com
  - [ ] **New +** → **Web Service**
  - [ ] Conectar repositorio GitHub
  - [ ] Seleccionar rama: `main`

- [ ] **Configurar Build y Start**
  - [ ] Build Command:
    ```
    pip install -r requirements.txt && cd app && python manage.py collectstatic --noinput
    ```
  - [ ] Start Command:
    ```
    gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
    ```
  - [ ] Runtime: Python 3

- [ ] **Agregar Base de Datos**
  - [ ] Haz clic en **Add Database**
  - [ ] Type: PostgreSQL
  - [ ] Database Name: portfolio_db
  - [ ] User: (por defecto)
  - [ ] Render crea automáticamente DATABASE_URL

- [ ] **Configurar Variables de Entorno**
  En **Environment** → **Add Environment Variables**:
  
  ```
  SECRET_KEY = <generada_con_django>
  DEBUG = false
  ALLOWED_HOSTS = tu-app.onrender.com,www.tu-app.onrender.com,localhost
  DJANGO_SETTINGS_MODULE = app.settings
  ```
  
  Para generar SECRET_KEY:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **Crear Web Service**
  - [ ] Verifica todas las configuraciones
  - [ ] Haz clic en **Create Web Service**

## 🚀 Fase 3: Deploy Inicial

- [ ] **Push a GitHub**
  ```bash
  git push origin main
  ```

- [ ] **Esperar que Render haga deploy**
  - [ ] Ir a **Logs** en el Web Service
  - [ ] Esperar que diga "Service is live"
  - [ ] Típicamente toma 5-10 minutos

- [ ] **Verificar que la app está corriendo**
  - [ ] Abre tu URL de Render (ej: https://portfolio.onrender.com)
  - [ ] Deberías ver la página principal (aunque sin datos aún)

## 📊 Fase 4: Inicializar Base de Datos

- [ ] **Conectarse a Render Shell**
  - [ ] En tu Web Service
  - [ ] Haz clic en **Shell** (arriba a la derecha)

- [ ] **Ejecutar inicializador**
  ```bash
  cd /app
  python manage.py shell < init_render_db.py
  ```
  - [ ] Migraciones ejecutadas
  - [ ] Superuser creado (admin / ChangeMeImmediately123!)
  - [ ] Archivos estáticos recolectados

- [ ] **Cargar datos** (si tienes datos_full.json)
  ```bash
  python manage.py loaddata datos_full.json --verbosity 2
  ```
  - [ ] Todos los datos cargados exitosamente

- [ ] **Cambiar contraseña del admin**
  ```bash
  python manage.py changepassword admin
  ```
  - [ ] Ingresa una contraseña segura
  - [ ] Confirma

## ✨ Fase 5: Verificaciones Finales

- [ ] **Acceder a /admin**
  - [ ] URL: https://tu-app.onrender.com/admin
  - [ ] Username: admin
  - [ ] Password: la que acabas de cambiar
  - [ ] Verifica que ves tus datos

- [ ] **Verificar funcionalidades**
  - [ ] Home page carga correctamente
  - [ ] Skills visibles
  - [ ] Experiencias visibles
  - [ ] Proyectos visibles
  - [ ] Datos están correctos

- [ ] **Verificar archivos estáticos**
  - [ ] CSS cargados correctamente (página no se ve rota)
  - [ ] Imágenes/fotos visibles
  - [ ] Icons de Font Awesome (si los usas)

- [ ] **Verificar HTTPS**
  - [ ] URL muestra 🔒 (HTTPS seguro)
  - [ ] Certificado SSL válido

## 🔒 Fase 6: Seguridad

- [ ] **Verificar DEBUG = false**
  - [ ] Ir a Environment variables
  - [ ] Confirmar DEBUG=false

- [ ] **Verificar SECRET_KEY**
  - [ ] Es una clave larga y aleatoria
  - [ ] NO es la default de Django

- [ ] **ALLOWED_HOSTS configurados**
  - [ ] Incluye tu dominio final de Render

- [ ] **Cambiar contraseña admin**
  - [x] Ya hecho en Fase 4

- [ ] **Email configurado (opcional)**
  - [ ] Si tienes formulario de contacto
  - [ ] Configurar EMAIL_BACKEND en variables

## 🔄 Fase 7: Mantenimiento Continuo

- [ ] **Crear backup de BD**
  ```bash
  ./deploy-render.sh backup
  ```

- [ ] **Configurar monitoreo**
  - [ ] Revisar logs regularmente
  - [ ] Configurar alertas si es necesario

- [ ] **Plan de actualizaciones**
  - [ ] Cambios locales → Git push
  - [ ] Render automáticamente hace deploy
  - [ ] Monitorear logs durante deploy

## 📝 Notas Importantes

- Render monitorea tu rama `main` y automáticamente hace deploy
- Si haces cambios en producción, cópialos a local y luego push
- Los logs están disponibles 24/7 en el Dashboard
- La BD PostgreSQL tiene backup automático

## 🆘 Si Algo Sale Mal

1. **Revisa los logs**
   - Web Service → Logs
   - Busca errores específicos

2. **Problemas comunes**:
   - **ModuleNotFoundError**: Falta dependency en requirements.txt
   - **Database connection error**: Verifica DATABASE_URL
   - **Migration error**: Ejecuta `python manage.py migrate` en Shell
   - **Static files missing**: Ejecuta `python manage.py collectstatic --noinput`

3. **Contacta soporte de Render**
   - https://render.com/support

## ✅ ¡DEPLOYMENT COMPLETADO!

Cuando todo esté hecho, felicidades! 🎉

Tu portfolio está ahora desplegado en Render.com y es:
- ✅ Accesible desde internet
- ✅ Seguro (HTTPS)
- ✅ Respaldado automáticamente
- ✅ Escalable automáticamente

---

**Fecha de inicio**: 21 de Diciembre de 2025  
**Estado**: Listo para comenzar deploy
