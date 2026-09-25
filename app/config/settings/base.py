"""
Django Settings - Base configuration (shared across all environments).

This file contains common settings used by all environments.
Environment-specific overrides are in: development.py, production.py, testing.py
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# ============================================================================
# BUILD PATHS & ENVIRONMENT SETUP
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ============================================================================
# LOGGING SETUP
# ============================================================================

from app.config.logging_config import setup_logging

# DEBUG se define después, pero inicializamos logging aquí
# (será sobrescrito en los settings específicos)
_DEBUG_DEFAULT = os.getenv('DEBUG', 'False') == 'True'
setup_logging(debug=_DEBUG_DEFAULT)

# ============================================================================
# CORE SETTINGS (COMMON)
# ============================================================================

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-change-in-prod')

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# --- SEO & LOCALIZATION ---
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

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
    'rest_framework',
    'app.landing',
    'app.gym',
    'app.prompts',
    'app.documentum.apps.DocumentumConfig',
    'app.blog',
    'app.analytics',
    'app.utils.apps.UtilsConfig',
    # 'components_ui'  # TODO: Instalar vía SSH: pip install git+ssh://...
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'csp.middleware.CSPMiddleware',
    'app.config.middleware.CSPNonceMiddleware',  # Must be after CSPMiddleware
    'app.analytics.middleware.AnalyticsTrackingMiddleware',
]

# ── TECH-003: Content Security Policy (Report-Only mode) ──────────────────────────
# REVERTIDO a Report-Only: Detectados problemas con nonce rendering en producción.
# TODO: Implementar nonce correctamente en FIX #3 (próxima iteración).
# Por ahora, solo reportamos violaciones sin bloquear (más seguro que romper el sitio).
CONTENT_SECURITY_POLICY_REPORT_ONLY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "'unsafe-inline'",          # CKEditor, AOS inline init (temporal)
            "www.google.com",           # reCAPTCHA
            "www.gstatic.com",          # reCAPTCHA
            "raw.githubusercontent.com",  # CDN logos
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",          # estilos inline necesarios (componentes Bootstrap, inline en templates)
            "fonts.googleapis.com",
        ],
        "font-src": [
            "'self'",
            "fonts.gstatic.com",
        ],
        "img-src": [
            "'self'",
            "data:",
            "raw.githubusercontent.com",  # CDN imágenes
            "*.supabase.co",            # por si hay media en Supabase
        ],
        "connect-src": ["'self'"],
        "frame-src": [
            "www.google.com",           # reCAPTCHA iframe
        ],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "report-uri": ["/csp-report/"],
    },
}

ROOT_URLCONF = 'app.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.config.context_processors.brand_assets',
                'app.config.context_processors.csp_nonce',  # CSP nonce para scripts inline
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

# --- STATIC & MEDIA FILES ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_MAX_AGE = 31536000
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

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
LOGIN_URL = 'login'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '200/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# ── TECH-004: Celery Configuration (Async Tasks) ──────────────────────────
# Celery es usado para procesar tareas asincrónicas como batch de analytics.
# Broker: Redis (producción), puede ser in-memory en desarrollo.
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos max
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_EXPIRES = 3600  # 1 hora

# Analytics: tamaño de batch antes de enviar a Celery (evita overhead)
ANALYTICS_BATCH_SIZE = 10

# En desarrollo/testing, hacer tareas eager (sincrónico) para debugging
if DEBUG:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
