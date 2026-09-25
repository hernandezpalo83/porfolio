import requests
import logging
import ipaddress
from functools import lru_cache

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """Obtener IP del cliente considerando proxies (validado)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

    # Validar que sea un IP válido
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return '0.0.0.0'


@lru_cache(maxsize=1000)
def get_country_from_ip(ip: str) -> str:
    """
    Obtener país de IP usando ip-api.com (caché de 1000 IPs).
    Privacy-first: sin cookies, solo detecta país anónimamente.
    SECURITY: IP validado antes de usarlo en la URL (previene SSRF).
    """
    if ip in ['0.0.0.0', '127.0.0.1', 'localhost']:
        return 'XX'

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        logger.warning(f"IP inválida recibida: {ip}")
        return 'XX'

    try:
        response = requests.get(
            f'https://ip-api.com/json/{ip}?fields=countryCode',
            timeout=2
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('countryCode', 'XX')
    except Exception as e:
        logger.warning(f"Error detectando país de {ip}: {e}")

    return 'XX'


def detect_device(user_agent: str) -> str:
    """Detectar tipo de dispositivo desde User-Agent."""
    ua = user_agent.lower()

    if 'mobile' in ua or 'android' in ua or 'iphone' in ua or 'ipod' in ua:
        return 'mobile'
    elif 'tablet' in ua or 'ipad' in ua or 'kindle' in ua:
        return 'tablet'
    else:
        return 'desktop'


def calculate_trending_score(views_7d: int, unique_visitors: int, bounce_rate: float) -> float:
    """
    Calcular score de trending basado en:
    - Vistas en últimos 7 días
    - Visitantes únicos
    - Bounce rate (penaliza alto bounce)

    Score: 0-100
    """
    if views_7d == 0:
        return 0.0

    base_score = min(views_7d / 10, 40)  # Máx 40 por vistas
    visitor_score = min(unique_visitors / 5, 30)  # Máx 30 por visitantes
    bounce_penalty = (bounce_rate / 100) * 30  # Penaliza hasta -30

    score = base_score + visitor_score - bounce_penalty
    return max(0.0, min(100.0, score))
