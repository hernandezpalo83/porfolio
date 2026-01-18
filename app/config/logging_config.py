"""
Configuración centralizada de logging para el proyecto.
Reemplaza print() y proporciona trazas estructuradas.
"""

import logging
import logging.config
import os
from pathlib import Path

# Obtener BASE_DIR sin acceder a django.conf.settings
# (para evitar circular imports durante la inicialización)
BASE_DIR = Path(__file__).resolve().parent.parent


def get_logging_config(debug: bool = False):
    """
    Retorna la configuración de logging según el entorno.
    
    Args:
        debug: Si True, usa configuración verbose; si False, configuración de producción
    """
    logs_dir = os.path.join(BASE_DIR, 'logs')
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[{levelname}] {asctime} {name} {funcName}:{lineno} - {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '[{levelname}] {name} - {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'level': 'DEBUG',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_dir, 'django.log'),
                'maxBytes': 1024 * 1024 * 10,  # 10 MB
                'backupCount': 5,
                'formatter': 'verbose',
                'level': 'INFO',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'] if not debug else ['console'],
                'level': 'DEBUG' if debug else 'INFO',
                'propagate': False,
            },
            'app.landing': {
                'handlers': ['console', 'file'] if not debug else ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'app.prompts': {
                'handlers': ['console', 'file'] if not debug else ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'app.blog': {
                'handlers': ['console', 'file'] if not debug else ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'app.gym': {
                'handlers': ['console', 'file'] if not debug else ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }


def setup_logging(debug: bool = False):
    """
    Inicializa la configuración de logging.
    
    Args:
        debug: Si True, usa configuración verbose
    """
    logs_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    config = get_logging_config(debug=debug)
    logging.config.dictConfig(config)
