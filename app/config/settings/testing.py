"""
Django Settings - Testing configuration.

Used for running test suites. Optimized for speed and isolation.
"""

from .base import *

DEBUG = True

# Reemplazar el paquete privado por el stub local para CI (sin acceso a GitHub)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'components_ui']
INSTALLED_APPS.append('app.components_ui_stub')

# Faster password hashing in testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast for testing only
]

# In-memory database for testing (much faster)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Override STORAGES to use local storage for tests (avoid WhiteNoise manifest errors)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Disable migrations for faster tests (if applicable)
# WARNING: Only use if you're confident in your schema
# MIGRATION_MODULES = {
#     'app': None,
# }

# Simple logging for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'DEBUG',
    },
}

if __name__ == '__main__':
    print("✓ Testing settings loaded")
