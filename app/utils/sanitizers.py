"""
HTML Sanitization utilities for protecting against XSS attacks.

Uses bleach library to safely clean HTML content from CKEditor and other sources,
allowing only whitelisted tags and attributes.
"""

import logging
from bleach import clean, ALLOWED_TAGS as BLEACH_ALLOWED_TAGS

logger = logging.getLogger(__name__)

# Allowed HTML tags for content rendered with |sanitize_html
# Conservative whitelist: allows formatting, lists, and links only
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'del', 'ins',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'blockquote',
    'code', 'pre',
    'a',
    'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'hr',
]

# Allowed attributes per tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],
    'tr': [],
    'th': [],
    'td': [],
}


def sanitize_html(html_content: str) -> str:
    """
    Sanitize HTML content using bleach library.

    Removes all HTML tags and attributes not in the whitelist.
    Strips dangerous protocols (javascript:, data:, etc).

    Args:
        html_content (str): Raw HTML content from CKEditor or similar sources.

    Returns:
        str: Cleaned, safe HTML content.

    Example:
        >>> html = '<p>Safe <script>alert("XSS")</script></p>'
        >>> sanitize_html(html)
        '<p>Safe &lt;script&gt;alert("XSS")&lt;/script&gt;</p>'
    """
    if not html_content:
        return ''

    try:
        # Clean with whitelist, strip disallowed tags, convert to text
        cleaned = clean(
            html_content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
            strip_comments=True,
        )
        logger.debug(f"Sanitized HTML: {len(html_content)} → {len(cleaned)} chars")
        return cleaned
    except Exception as e:
        logger.error(f"Error sanitizing HTML: {e}", exc_info=True)
        # Fallback: return the input with dangerous tags stripped
        return clean(html_content, tags=[], strip=True)
