import re
from datetime import date, datetime
import math
from django.utils import timezone
from django.utils.text import slugify

def fecha_utc(fecha: date) -> datetime:
    """Convierte una fecha a datetime UTC."""
    if isinstance(fecha, datetime):
        return timezone.make_aware(fecha, timezone.utc) if timezone.is_naive(fecha) else fecha
    return timezone.make_aware(datetime.combine(fecha, datetime.min.time()), timezone.utc)

def fecha_utc_string(fecha: date) -> str:
    """Devuelve la fecha en formato YYYY-MM-DD."""
    return fecha.strftime('%Y-%m-%d') if fecha else ''

def fecha_formateada(fecha: date, formato: str = '%d/%m/%Y') -> str:
    """Devuelve la fecha en el formato especificado."""
    return fecha.strftime(formato) if fecha else ''

def fecha_sin_dia(fecha: date) -> str:
    """Devuelve MM/YYYY."""
    return fecha.strftime('%m/%Y') if fecha else ''

def esta_vacio(valor) -> bool:
    """Comprueba si un valor está vacío (None, string vacío, lista vacía)."""
    if valor is None:
        return True
    if isinstance(valor, str) and not valor.strip():
        return True
    if isinstance(valor, (list, tuple, dict)) and not valor:
        return True
    return False

def es_hora_minuto_segundo(texto: str) -> bool:
    """Valida si un texto tiene el formato HH:MM:SS."""
    patron = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
    return bool(re.match(patron, texto)) if texto else False

def convertir_a_segundos(hora: str) -> int:
    """Convierte 'HH:MM:SS' a segundos totales."""
    if not hora or not es_hora_minuto_segundo(hora):
        return 0
    h, m, s = map(int, hora.split(':'))
    return h * 3600 + m * 60 + s

def convertir_a_hora_minuto_segundo(seg: int) -> str:
    """Convierte segundos totales a 'HH:MM:SS'."""
    if seg is None or seg < 0:
        return "00:00:00"
    m, s = divmod(seg, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

def formatear_numero(valor: float, decimales: int = 2, idioma: str = 'es') -> str:
    """Formatea un número con separador de miles y decimales según idioma."""
    if valor is None:
        return ""
    try:
        if idioma == 'es':
            formato = f"{{:,.{decimales}f}}"
            return formato.format(float(valor)).replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            formato = f"{{:,.{decimales}f}}"
            return formato.format(float(valor))
    except (ValueError, TypeError):
        return str(valor)

def redondear(numero: float, decimales: int = 2) -> float:
    """Redondea un número al número de decimales especificado."""
    if numero is None:
        return 0.0
    factor = 10 ** decimales
    return math.floor(numero * factor + 0.5) / factor

def limpiar_cadena(cadena: str) -> str:
    """Elimina acentos y caracteres especiales básicos."""
    if not cadena:
        return ""
    import unicodedata
    cadena = unicodedata.normalize('NFKD', cadena).encode('ASCII', 'ignore').decode('utf-8')
    return cadena

def url_slug(texto: str) -> str:
    """Convierte texto en slug para URLs."""
    return slugify(texto)

def get_colores_disponibles() -> list:
    """Devuelve los colores estándar del sistema."""
    return ['primary', 'secondary', 'error', 'warning', 'success', 'info', 'neutral']

def usuario_tiene_permiso(user, permisos: list) -> bool:
    """
    Comprueba si un usuario tiene todos/algún permiso de la lista.
    Asumimos ANY match (como un OR).
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return any(user.has_perm(permiso) for permiso in permisos)
