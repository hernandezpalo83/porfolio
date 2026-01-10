import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = os.getenv('DEBUG', 'True') == 'True'

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-this')

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# CSRF Config
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = [
        "https://porfolio.hernandezpalo.es",
        "https://porfolio-polished-water-5224.fly.dev",
    ]

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage', 
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

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise siempre después de Security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'app.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.config.context_processors.brand_assets',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.config.wsgi.application'

# --- DATABASE ---
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.config(default=database_url, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- STATIC FILES (WhiteNoise) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []
# Esto asegura que WhiteNoise maneje los CSS/JS sin interferencia de Cloudinary
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- MEDIA FILES (Cloudinary vs Local) ---
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

if not DEBUG:
    # Producción: Las imágenes a Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/' # URL lógica
else:
    # Desarrollo: Las imágenes a tu carpeta media local
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- OTROS CONFIGS ---
LOGIN_REDIRECT_URL = 'private' 
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = '/'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

CKEDITOR_5_UPLOAD_PATH = "uploads/"
if not DEBUG:
    CKEDITOR_5_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "link", "bulletedList", 
            "numberedList", "blockQuote", "|", 'imageUpload', "undo", "redo", "|", "sourceEditing" 
        ],
        "height": 300,
        "width": "100%",
    }
}

# Brand Assets
BRAND_ASSETS_URL = "https://raw.githubusercontent.com/hernandezpalo83/cdn/main"
PERSONAL_BRAND = {
    "PROFILE_PICTURE": f"{BRAND_ASSETS_URL}/profile/Foto_perfil2.jpeg",
    "AVATAR": f"{BRAND_ASSETS_URL}/profile/avatar.png",
    "LOGO": f"{BRAND_ASSETS_URL}/logos/logo-main.svg",
    "BANNER": f"{BRAND_ASSETS_URL}/banners/linkedin-header.png",
}

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY = str(os.getenv('RECAPTCHA_PUBLIC_KEY', ''))
RECAPTCHA_PRIVATE_KEY = str(os.getenv('RECAPTCHA_PRIVATE_KEY', ''))
RECAPTCHA_V3_ACTION = 'contact_form'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
RECAPTCHA_TESTING = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'