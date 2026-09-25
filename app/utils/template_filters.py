"""
Custom Django template filters for security and formatting.

Filters should be used in templates via: {% load template_filters %}
Example: {{ content|sanitize_html }}
"""

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from .sanitizers import sanitize_html

register = template.Library()


@register.filter
@stringfilter
def sanitize_html_filter(value):
    """
    Template filter that sanitizes HTML content to prevent XSS attacks.

    Replaces the dangerous |safe filter with safe sanitization.
    Only allows whitelisted HTML tags (see sanitizers.py for list).

    Usage in templates:
        {{ document.content|sanitize_html }}

    This filter automatically marks the result as safe for Django's template engine,
    so you don't need to add |safe afterwards.

    Args:
        value (str): Raw HTML content

    Returns:
        SafeString: Cleaned HTML marked as safe
    """
    cleaned = sanitize_html(value)
    return mark_safe(cleaned)


# Alias for convenience
register.filter('sanitize_html', sanitize_html_filter)
