"""
Django Settings - Production configuration.

Used in production (Render, AWS, etc). Strict security, DEBUG=False.
"""

from .base import *

# --- SENTRY (error monitoring) ---
# NOTE: sentry-sdk[django]>=2.0 is in requirements.txt and MUST be installed
# If missing, it indicates a deployment issue (pip install not running properly)
try:
    import sentry_sdk
    _sentry_dsn = os.getenv('SENTRY_DSN', '')
    if _sentry_dsn:
        sentry_sdk.init(
            dsn=_sentry_dsn,
            traces_sample_rate=0.1,
            environment='production',
            send_default_pii=False,
        )
except ImportError as e:
    # Fallback: If sentry-sdk is missing, continue but log warning
    # This should NOT happen in production if pip install is working
    import sys
    print(f"WARNING: sentry-sdk not installed. Check requirements.txt installation.", file=sys.stderr)
    pass

DEBUG = False

# --- SECURITY (PRODUCTION HARDENING) ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF trusted origins from environment
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_env.split(',')]
else:
    # Fallback: update with your production domains
    CSRF_TRUSTED_ORIGINS = [
        "https://hernandezpalo.es",
        "https://www.hernandezpalo.es",
    ]

# Password validation enabled in production
AUTH_PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]

# Logging to file and syslog in production

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
            'level': 'ERROR',  # Only log errors and above to console (visible in Render)
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_production.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

if __name__ == '__main__':
    print("✓ Production settings loaded")
