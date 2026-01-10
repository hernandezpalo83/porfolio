import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- SEGURIDAD ---
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key-cambiar-en-produccion')
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,hernandezpalo.es,.render.com").split(",")

# --- APPS (Orden estricto) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',           # DEBE ir antes de staticfiles si quieres control total
    'django.contrib.staticfiles',
    'cloudinary',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'app.config.urls'

# --- DATABASE ---
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {'default': dj_database_url.config(default=database_url, conn_max_age=600)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

# --- STATIC FILES (WhiteNoise) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'app', 'landing', 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CLOUDINARY (SIN CONDICIONALES) ---
# Forzamos Cloudinary para TODO: local y producción
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Almacenamiento por defecto para ImageField y FileField
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Almacenamiento específico para CKEditor 5
CKEDITOR_5_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/' # Cloudinary lo interceptará

# --- CKEDITOR 5 CONFIG ---
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": ["heading", "|", "bold", "italic", "link", "imageUpload", "sourceEditing"],
        "image": {
            "toolbar": ["imageTextAlternative", "|", "imageStyle:alignLeft", "imageStyle:alignCenter", "imageStyle:alignRight"],
            "styles": ["alignLeft", "alignCenter", "alignRight"]
        },
    }
}
CKEDITOR_5_UPLOAD_PATH = "blog/"

# --- RECAPTCHA ---
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')
RECAPTCHA_TESTING = DEBUG

# --- TEMPLATES ---
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

CSRF_TRUSTED_ORIGINS = ["https://hernandezpalo.es", "https://porfolio.hernandezpalo.es"]
SITE_ID = 1
CRISPY_TEMPLATE_PACK = 'bootstrap5'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Assets de marca
BRAND_ASSETS_URL = "https://raw.githubusercontent.com/hernandezpalo83/cdn/main"
PERSONAL_BRAND = {
    "PROFILE_PICTURE": f"{BRAND_ASSETS_URL}/profile/Foto_perfil2.jpeg",
    "AVATAR": f"{BRAND_ASSETS_URL}/profile/avatar.png",
    "LOGO": f"{BRAND_ASSETS_URL}/logos/logo-main.svg",
}