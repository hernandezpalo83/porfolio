"""
Custom middleware for security enhancements.

Includes:
- CSP Nonce generation for inline scripts
- Security headers
"""

import secrets
from django.utils.deprecation import MiddlewareMixin


class CSPNonceMiddleware(MiddlewareMixin):
    """
    Generate a unique Content Security Policy nonce for each request.

    The nonce is used in CSP to allow specific inline scripts while still
    protecting against XSS attacks. Must be used with django-csp middleware.

    Usage in templates:
        <script nonce="{{ request.csp_nonce }}">...</script>

    Usage in CSP settings:
        "script-src": ["'self'", "'nonce-{{ request.csp_nonce }}'", ...]

    The nonce is a random 16-byte value encoded as URL-safe base64.
    """

    NONCE_LENGTH = 16  # 128-bit nonce (standard is 12-16 bytes)

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Generate nonce as URL-safe base64 string (no padding)
        nonce = secrets.token_urlsafe(self.NONCE_LENGTH).rstrip('=')
        request.csp_nonce = nonce

        response = self.get_response(request)

        # Inject nonce into CSP headers if present
        # django-csp sets the header, but we need to replace the nonce placeholder
        for header in ['Content-Security-Policy', 'Content-Security-Policy-Report-Only']:
            if header in response:
                csp_value = response[header]
                # Replace nonce placeholder with actual nonce
                csp_value = csp_value.replace('{{ csp_nonce }}', f"'{nonce}'")
                csp_value = csp_value.replace('{{{ csp_nonce }}}', f"'{nonce}'")
                response[header] = csp_value

        return response
