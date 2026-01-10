import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- CONFIGURACIÓN DE ENTORNO ---
# Por seguridad, si no existe la variable, es False.
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key-hernandezpalo')
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,hernandezpalo.es").split(",")

# --- SILENCIAR ERRORES DE SISTEMA ---
SILENCED_SYSTEM_CHECKS = [
    'django_recaptcha.recaptcha_test_key_error',
    'captcha.recaptcha_test_key_error'
]

# --- APPS (Orden Crítico para Cloudinary + StaticFiles) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # 1. Estáticos base
    'cloudinary_storage',           # 2. Almacenamiento (Debe ir antes de cloudinary)
    'cloudinary',                   # 3. API
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_tables2',
    'django_filters',
    'django_htmx',
    'crispy_forms',
    'crispy_bootstrap5', 
    'django_ckeditor_5',
    'django_recaptcha',
    'app.landing',
    'app.gym',
    'app.prompts',
    'app.blog',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Gestión de CSS/JS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'app.config.urls'

# --- BASE DE DATOS ---
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {'default': dj_database_url.config(default=database_url, conn_max_age=600)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

# --- ARCHIVOS ESTÁTICOS (WhiteNoise para CSS/JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Lógica flexible para encontrar la carpeta static de landing
possible_static_path = os.path.join(BASE_DIR, 'app', 'landing', 'static')
if os.path.exists(possible_static_path):
    STATICFILES_DIRS = [possible_static_path]
else:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'landing', 'static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- ALMACENAMIENTO MEDIA (Cloudinary Unificado) ---
# Usamos Cloudinary SIEMPRE (Local y Producción)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    'STATICFILES_STORAGE': None, # Cloudinary no toca los CSS
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/' # Cloudinary gestionará la URL final automáticamente

# --- CKEDITOR 5 (Configuración Unificada) ---
CKEDITOR_5_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
CKEDITOR_5_UPLOAD_PATH = "blog/" # Carpeta dentro de Cloudinary
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": ["heading", "|", "bold", "italic", "link", "imageUpload", "sourceEditing"],
        "alignment": {"options": ["left", "center", "right", "justify"]},
    }
}

# --- RECAPTCHA ---
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')
RECAPTCHA_TESTING = DEBUG

# --- OTROS ---
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'app.config.context_processors.brand_assets',
    ]},
}]

CSRF_TRUSTED_ORIGINS = [
    "https://porfolio.hernandezpalo.es",
    "https://porfolio-polished-water-5224.fly.dev",
]

SITE_ID = 1
CRISPY_TEMPLATE_PACK = 'bootstrap5'
LOGIN_REDIRECT_URL = 'private'
LOGOUT_REDIRECT_URL = '/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BRAND_ASSETS_URL = "https://raw.githubusercontent.com/hernandezpalo83/cdn/main"
PERSONAL_BRAND = {
    "PROFILE_PICTURE": f"{BRAND_ASSETS_URL}/profile/Foto_perfil2.jpeg",
    "AVATAR": f"{BRAND_ASSETS_URL}/profile/avatar.png",
    "LOGO": f"{BRAND_ASSETS_URL}/logos/logo-main.svg",
}