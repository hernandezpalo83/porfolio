"""
Django Settings - Modularized configuration system.

This module loads environment-specific settings based on DJANGO_ENV.
Recommended environments: 'development', 'production', 'testing'

Usage:
    Set DJANGO_ENV environment variable before starting Django.
    Default: development (for security in production, must be explicitly set)
"""

import os
import sys

# Determine which settings to load
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development').lower()

# Auto-detect test runner
_is_testing = 'test' in sys.argv

if DJANGO_ENV == 'production':
    from .production import *
elif DJANGO_ENV == 'testing' or _is_testing:
    from .testing import *
else:
    # Default to development
    from .development import *
