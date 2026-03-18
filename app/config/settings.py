"""
Django settings for app project.
Optimized for Performance (TPM Standard) - HernandezPalo Portfolio
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url
import logging.config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Setup logging configuration
from app.config.logging_config import setup_logging
setup_logging()

# --- CORE SETTINGS ---
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-in-prod')

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# --- SEO & LOCALIZATION ---
# IMPORTANTE: Si tu contenido es en español, cámbialo a 'es'. Google lo usa para indexar.
LANGUAGE_CODE = 'es-es' 
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# --- SECURITY (SEO BOOST) ---
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',')]
else:
    CSRF_TRUSTED_ORIGINS = [
        "https://porfolio.hernandezpalo.es",
        "https://porfolio-polished-water-5224.fly.dev",
    ]

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_tables2',
    'django_filters',
    'django_htmx',
    'crispy_forms',
    'crispy_bootstrap5', 
    'django_ckeditor_5',
    'django_recaptcha',
    'htmlmin',  # Minificador HTML
    'app.landing',
    'app.gym',
    'app.prompts',
    'app.documentum.apps.DocumentumConfig',
    'app.blog',
    'app.metadata_manager.apps.ListaConfig',
    'rest_framework',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware', # 1. Comprime todo para ahorrar ancho de banda
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 2. Sirve estáticos eficientemente
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware', # 3. Minifica el HTML final
]

ROOT_URLCONF = 'app.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.config.context_processors.brand_assets',
                'app.landing.context_processors.menu_int_processor',
                'app.documentum.context_processors.docs_navigation',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.config.wsgi.application'

# --- DATABASE ---
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- STATIC & MEDIA FILES (PERFORMANCE CORE) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise Optimization: Cache eterno para archivos con hash
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_MAX_AGE = 31536000 # 1 año de caché
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

WHITENOISE_KEEP_ONLY_HASHED_FILES = True

# --- HTML MINIFICATION ---
HTML_MINIFY = not DEBUG # Solo en producción
HTML_MINIFY_KEEP_COMMENTS = False # Eliminar comentarios

# --- THIRD PARTY CONFIGS ---
CRISPY_TEMPLATE_PACK = 'bootstrap5'

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "link", "|",
            "bulletedList", "numberedList", "blockQuote", "|",
            "insertImage", "undo", "redo", "|", "sourceEditing" 
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative", "|", 
                "imageStyle:alignLeft", "imageStyle:alignCenter", "imageStyle:alignRight"
            ],
            "styles": ["alignLeft", "alignCenter", "alignRight"],
            "insert": { "integrations": ["url"] }
        },
        "height": 300,
        "width": "100%",
    }
}

# Assets y Captcha
BRAND_ASSETS_URL = "https://raw.githubusercontent.com/hernandezpalo83/cdn/main"
PERSONAL_BRAND = {
    "PROFILE_PICTURE": f"{BRAND_ASSETS_URL}/profile/Foto_perfil2.webp",
    "AVATAR": f"{BRAND_ASSETS_URL}/profile/avatar.png",
    "LOGO": f"{BRAND_ASSETS_URL}/logos/logo-main.svg",
    "BANNER": f"{BRAND_ASSETS_URL}/banners/linkedin-header.png",
}

RECAPTCHA_PUBLIC_KEY = str(os.getenv('RECAPTCHA_PUBLIC_KEY', ''))
RECAPTCHA_PRIVATE_KEY = str(os.getenv('RECAPTCHA_PRIVATE_KEY', ''))
RECAPTCHA_V3_ACTION = 'contact_form'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'landing:private_area'
LOGOUT_REDIRECT_URL = '/'

# --- LOGGING CONFIGURATION ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module}.{funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'production_console': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Root logger - captura todo
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # Django core
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Errores de Django (500s, etc)
        'django.request': {
            'handlers': ['console', 'production_console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Queries SQL (solo en DEBUG)
        'django.db.backends': {
            'handlers': ['console_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Admin actions
        'django.contrib.admin': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Tu aplicación
        'app.landing': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'app.blog': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
LOGIN_URL = 'login'