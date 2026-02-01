# 🚀 Portfolio Profesional - Javier Hernández Martin

Este proyecto es mi **portfolio profesional y plataforma técnica**, diseñado para centralizar mi experiencia, proyectos de desarrollo y una **biblioteca especializada de prompts** para Product Managers.  
Construido con **Django 5.1** y PostgreSQL (ahora gestionada en **Supabase**), desplegado de forma automatizada en **Render**.

🌐 **Sitio en vivo:**  
Hernandezpalo.es

---

## 🛠️ Tecnologías Aplicadas

### **Backend & Lógica**
- **Python 3.11+**: Lenguaje principal para lógica de negocio y scripts de administración.
- **Django 5.1**: Framework robusto para gestión de datos, seguridad y routing.
- **Django Sites & Sitemaps**: SEO dinámico y gestión avanzada de URLs.
- **PostgreSQL (Supabase)**: Base de datos relacional, ahora con persistencia segura y pooler de sesión.

### **Frontend (Hybrid Architecture)**
- **Public Area (Landing/Blog)**: 
  - **Vanilla JS (ES6+)**: Cero dependencias (No jQuery) para máxima velocidad.
  - **Custom CSS (Kards)**: Diseño ligero con CSS moderno (`clamp`, `flexbox`).
  - **HTML Minification**: Compresión automática en producción.
- **Private Area (Portal)**: 
  - **Bootstrap 5**: Gestión eficiente de dashboards y formularios.
  - **Bootstrap Icons**: Librería de iconos vectoriales.

---

## 📁 Estructura del Proyecto (Django Apps)

- **app.landing**: Página principal, SEO, Open Graph y lógica del portafolio.  
- **app.prompts**: Biblioteca privada de prompts con autenticación para herramientas de IA.  
- **app.gym**: Módulo dedicado a seguimiento y lógica específica (en desarrollo).  
- **app.config**: Configuración central de Django (`settings.py`, `urls.py`, `wsgi.py`).

---

## 🚀 Despliegue en Render

El sitio sigue una **arquitectura CI/CD**:

- **Web Service**: Despliegue automático desde la rama `main`.  
- **Database**: PostgreSQL en **Supabase**, con session pooler y SSL obligatorio.  
- **Environment Variables**: Seguridad y parametrización mediante `.env`. Variables principales:
  - `DEBUG` = False en producción.
  - `SECRET_KEY` = gestionada de forma privada.
  - `DATABASE_URL` = conexión mediante `dj-database-url` con Supabase Pooler.
- **Archivos Estáticos**: Gestionados con WhiteNoise, optimizando CSS/JS.

### ✅ Deploy: seed y verificación de `wiki`

- Asegúrate de que `documentum_seed_postgres.sql` esté en la raíz del repositorio (o pásalo con `--seed-sql`).
- Ejecuta (one‑off en Render o localmente):

```bash
python manage.py setup_db --seed --seed-sql documentum_seed_postgres.sql --normalize --render
```

- Verificación rápida:
  - Revisa los logs del deploy: deberías ver "Archivo SQL encontrado" y "Found X documents to render".
  - Accede a `https://<tu-site>/wiki/` y prueba alguna página (p.ej. `/wiki/general/`) — debe devolver 200 y mostrar el contenido renderizado.

- Alternativa: si prefieres importar desde Markdown, puedes usar `python manage.py seed_documentum`.

---

## 📦 Gestión de Datos y Resiliencia

Se ha implementado un **sistema de backup y restauración JSON** para proteger la integridad del portfolio:

- **Generar copia**: Exporta todos los datos de `landing` y `gym` a `db_backup.json`.
- **Ver JSON**: Permite inspeccionar el contenido del backup desde la interfaz web.
- **Descargar**: Descarga la copia localmente para almacenamiento externo.
- **Restaurar datos**: Valida y carga automáticamente el JSON, garantizando resiliencia y continuidad.  

Esta funcionalidad asegura **Disaster Recovery** y demuestra experiencia en **gestión de productos técnicos** y **automatización de procesos críticos**.

---

## 📊 SEO y Datos del Portfolio

- **Sitemap XML**: `/sitemap.xml` generado dinámicamente para indexación.
- **Open Graph**: Mejora la presentación en LinkedIn y redes sociales.  
- **Datos Estructurados (JSON-LD)**: `@type: Person` para que motores de búsqueda identifiquen mi perfil profesional.

---

## 🛠️ Instalación Local

1. **Clonar repositorio**:
   ```bash
   git clone [url-del-repositorio]
   cd porfolio

Crear entorno virtual e instalar dependencias:

python -m venv venv

source venv/bin/activate  # En Windows: venv\Scripts\activate

pip install -r requirements.txt

Configurar variables de entorno: Crea un archivo .env en la raíz con tus credenciales locales.

Migraciones y ejecución:

python manage.py migrate

python manage.py runserver

Web:Hernandezpalo.es

Desarrollado con ❤️ por Javier Hernández Martin.


