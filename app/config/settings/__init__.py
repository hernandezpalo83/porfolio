"""
Django Settings - Modularized configuration system.

This module loads environment-specific settings based on DJANGO_ENV.
Recommended environments: 'development', 'production', 'testing'

Usage:
    Set DJANGO_ENV environment variable before starting Django.
    Default: development (for security in production, must be explicitly set)
"""

import os
from django.core.management import execute_from_command_line

# Determine which settings to load
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development').lower()

if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'testing':
    from .testing import *
else:
    # Default to development
    from .development import *
