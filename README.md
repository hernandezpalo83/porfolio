🚀 **Portfolio Profesional - Javier Hernández Martin**

Este proyecto es mi portafolio personal y plataforma técnica, diseñado para centralizar mi experiencia, proyectos de desarrollo y una biblioteca especializada de prompts para Product Managers. Construido con Django y desplegado de forma automatizada en Render.

🌐 **Sitio en vivo:**
[Enlace al sitio]

---

## 🛠️ Tecnologías Aplicadas

### **Backend & Lógica**
- **Python 3.11+**: Lenguaje principal.
- **Django 5.x**: Framework robusto para la gestión de datos, seguridad y routing.
- **Django Sites & Sitemaps**: Configuración avanzada de SEO dinámico.
- **PostgreSQL**: Base de datos relacional (gestionada en Render).

### **Frontend**
- **Bootstrap 5 / HTML5 / CSS3**: Diseño responsive y moderno.
- **Bootstrap Icons**: Librería de iconos vectoriales.
- **JSON dinámico**: Consumo de datos externos para la biblioteca de prompts.

---

## 📁 Estructura del Proyecto (Django Apps)
El proyecto está modularizado en aplicaciones independientes para facilitar el mantenimiento:

- **app.landing**: Gestiona la página principal (Home), el SEO, los metadatos Open Graph y la lógica del portafolio estático.
- **app.prompts**: Mi biblioteca privada de prompts. Implementa un sistema de autenticación para proteger el acceso a herramientas de IA personalizadas.
- **app.gym**: (En desarrollo/específico) Módulo dedicado a seguimiento o lógica específica.
- **app.config**: Directorio raíz con la configuración centralizada de Django (settings, urls, wsgi).

---

## 🚀 Despliegue en Render
El sitio está configurado bajo una arquitectura de Integración Continua (CI/CD):

- **Web Service**: Conectado a la rama `main` de este repositorio. Cada push dispara un nuevo despliegue automático.
- **Database**: Instancia de PostgreSQL persistente.
- **Environment Variables**: Uso estricto de variables de entorno para seguridad:
  - `DEBUG`: Desactivado en producción.
  - `SECRET_KEY`: Gestionada de forma privada en el dashboard de Render.
  - `DATABASE_URL`: Conexión automática mediante `dj-database-url`.
- **Static Files**: Gestión de archivos estáticos mediante WhiteNoise para servir CSS y JS eficientemente desde el servidor de aplicaciones.

---

## 📊 Datos del Portfolio & SEO
Este proyecto pone un foco especial en el posicionamiento técnico (SEO):

- **Sitemap XML**: Generado dinámicamente en `/sitemap.xml` para indexación en Google Search Console.
- **Open Graph**: Etiquetas personalizadas para que al compartir en LinkedIn se muestre una "card" profesional con descripción > 100 caracteres e imagen de marca.
- **Datos Estructurados**: Implementación de JSON-LD (`@type: Person`) para que los motores de búsqueda identifiquen mi perfil profesional directamente.

---

## 🛠️ Instalación en Local
Si deseas replicar este proyecto localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [url-del-repositorio]
Crear entorno virtual e instalar dependencias:

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

Configurar variables de entorno: Crea un archivo .env en la raíz con tus credenciales locales.

Migraciones y ejecución:

python manage.py migrate
python manage.py runserver

📧 Contacto
LinkedIn:

Web:

Desarrollado con ❤️ por Javier Hernández Martin.
