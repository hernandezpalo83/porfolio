"""UI helpers for public templates: SVG sprite icons and JSON-LD escaping."""
import html
import json
import re

from django import template
from django.utils.html import format_html, strip_tags
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

_JSON_SCRIPT_ESCAPES = {ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026'}


@register.simple_tag
def icon(name: str, css_class: str = "") -> SafeString:
    """{% icon "home" %} → <svg><use href="#i-home"></svg> from the sprite in base.html."""
    return format_html(
        '<svg class="icon {}" aria-hidden="true" focusable="false"><use href="#i-{}"></use></svg>',
        css_class,
        name,
    )


@register.filter
def json_str(value) -> SafeString:
    """Encode a value as a JSON literal that is safe inside <script type="application/ld+json">."""
    if value is None:
        value = ""
    return mark_safe(json.dumps(str(value), ensure_ascii=False).translate(_JSON_SCRIPT_ESCAPES))


_BLOCK_TAGS = re.compile(r'<\s*(br|/p|/li|/h[1-6]|/div)\b[^>]*>', re.IGNORECASE)


@register.filter
def plain_text(value) -> str:
    """Rich text → single-line plain text, keeping a space where <br>/<p>/<li> used to separate words."""
    text = strip_tags(_BLOCK_TAGS.sub(' ', str(value or '')))
    return ' '.join(html.unescape(text).split())
