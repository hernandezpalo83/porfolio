from django import template
from .utils import (
    fecha_formateada,
    formatear_numero,
    convertir_a_hora_minuto_segundo,
    url_slug
)

register = template.Library()

@register.filter(name='format_fecha')
def format_fecha(value, args='%d/%m/%Y'):
    """Filtra fecha. Uso: {{ valor|format_fecha:"%d/%m/%Y" }}"""
    return fecha_formateada(value, args)

@register.filter(name='format_numero')
def format_numero(value, args=2):
    """Filtra número. Uso: {{ valor|format_numero:2 }}"""
    try:
        decimales = int(args)
    except ValueError:
        decimales = 2
    return formatear_numero(value, decimales)

@register.filter(name='format_duracion')
def format_duracion(value):
    """Convierte segundos a HH:MM:SS"""
    try:
        segundos = int(value)
        return convertir_a_hora_minuto_segundo(segundos)
    except (ValueError, TypeError):
        return value

@register.filter(name='slug')
def slug_filter(value):
    """Convierte a slug"""
    return url_slug(value) if value else ''
