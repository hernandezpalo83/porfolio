"""
Filtros de plantilla para la app landing.
"""
from django import template

register = template.Library()


@register.filter(name='split')
def split_filter(value: str, delimiter: str = ',') -> list:
    """Divide una cadena por el delimitador dado.
    Uso: {{ project.categoria|split:"," }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]


@register.filter(name='strip')
def strip_filter(value: str) -> str:
    """Elimina espacios al inicio y al final de una cadena.
    Uso: {{ tag|strip }}
    """
    if not value:
        return ''
    return value.strip()
