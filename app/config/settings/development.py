"""
Django Settings - Development configuration.

Used for local development. Less strict security, DEBUG=True, verbose logging.
"""

from .base import *

DEBUG = True

# Passwords validation disabled for easier local development
AUTH_PASSWORD_VALIDATORS = []

# Security: Less strict in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allow all CSRF origins in development
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Verbose logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {funcName}:{lineno} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

if __name__ == '__main__':
    print("✓ Development settings loaded")
