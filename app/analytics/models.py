from django.conf import settings
from django.db import models

from app.blog.models import Post


class NetworkType(models.TextChoices):
    BUSINESS = 'business', 'Empresa u organización'
    CORPORATE_PROXY = 'corporate_proxy', 'Empresa (vía proxy corporativo)'
    EDUCATION = 'education', 'Universidad o centro educativo'
    GOVERNMENT = 'government', 'Administración pública'
    ISP = 'isp', 'Particular (operadora)'
    MOBILE = 'mobile', 'Particular (red móvil)'
    HOSTING = 'hosting', 'Centro de datos / bots'
    UNKNOWN = 'unknown', 'Desconocida'


class TrafficSource(models.TextChoices):
    CHANNEL = 'channel', 'Canal propio (?src=)'
    CAMPAIGN = 'campaign', 'Campaña (UTM)'
    EMAIL = 'email', 'Correo (webmail)'
    SOCIAL = 'social', 'Red social'
    SEARCH = 'search', 'Buscador'
    REFERRAL = 'referral', 'Otra web'
    INTERNAL = 'internal', 'Navegación interna'
    DIRECT = 'direct', 'Directo'


class Channel(models.Model):
    """Canal propio: un enlace fijo con ?src=<code> en LinkedIn, la firma de correo, el CV..."""
    code = models.SlugField(max_length=40, unique=True, verbose_name="Código",
                            help_text="Aparece en la URL: https://hernandezpalo.es/?src=codigo")
    name = models.CharField(max_length=100, verbose_name="Nombre", help_text="Ej: LinkedIn, Firma de correo, CV en PDF")
    notes = models.CharField(max_length=250, blank=True, default='', verbose_name="Dónde está puesto")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Canal"
        verbose_name_plural = "Canales"

    def __str__(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return f"{settings.SITE_URL}/?src={self.code}"


class NetworkLabel(models.Model):
    """Corrección manual de una red (ASN): nombre legible y tipo, prioritaria sobre la detección."""
    asn = models.PositiveIntegerField(unique=True, verbose_name="ASN")
    name = models.CharField(max_length=150, verbose_name="Nombre a mostrar")
    network_type = models.CharField(max_length=20, choices=NetworkType.choices, verbose_name="Tipo")
    notes = models.CharField(max_length=250, blank=True, default='', verbose_name="Notas")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Etiqueta de red"
        verbose_name_plural = "Etiquetas de red"

    def __str__(self) -> str:
        return f"AS{self.asn} → {self.name}"


class PageView(models.Model):
    """Registra cada vista de página (privacy-first, sin cookies)."""

    DEVICE_CHOICES = [
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
        ("desktop", "Desktop"),
    ]

    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, default="GET")
    country = models.CharField(max_length=2, null=True, blank=True)
    device = models.CharField(max_length=20, choices=DEVICE_CHOICES, default="desktop")
    referrer = models.CharField(max_length=500, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    pageview_id = models.UUIDField(null=True, blank=True, unique=True, editable=False,
                                   help_text="Enlaza las métricas de lectura enviadas por el navegador")
    visitor_id = models.CharField(max_length=32, blank=True, default='', db_index=True,
                                  help_text="Identificador anónimo mensual (no reversible)")
    referrer_domain = models.CharField(max_length=150, blank=True, default='')
    source = models.CharField(max_length=20, choices=TrafficSource.choices, default=TrafficSource.DIRECT)
    utm_source = models.CharField(max_length=100, blank=True, default='')
    utm_medium = models.CharField(max_length=100, blank=True, default='')
    utm_campaign = models.CharField(max_length=100, blank=True, default='')
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='pageviews')
    asn = models.PositiveIntegerField(null=True, blank=True)
    organization = models.CharField(max_length=150, blank=True, default='', db_index=True)
    network_type = models.CharField(max_length=20, choices=NetworkType.choices, default=NetworkType.UNKNOWN)
    scroll_depth = models.IntegerField(default=0, help_text="Porcentaje scrolleado (0-100)")
    time_spent = models.IntegerField(default=0, help_text="Segundos en la página")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['path', '-timestamp']),
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['country', '-timestamp']),
            models.Index(fields=['visitor_id', '-timestamp']),
            models.Index(fields=['network_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.path} → {self.country} ({self.device})"


class SessionTracker(models.Model):
    """Agrupa PageViews por sesión para calcular duración y bounce rate."""

    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    device = models.CharField(max_length=20, default="desktop")
    referrer = models.CharField(max_length=500, null=True, blank=True)
    first_page = models.CharField(max_length=500)
    last_page = models.CharField(max_length=500)
    page_count = models.IntegerField(default=1)
    total_duration = models.IntegerField(default=0, help_text="Segundos totales")
    is_bounce = models.BooleanField(default=True, help_text="True si solo visitó 1 página")
    visitor_id = models.CharField(max_length=32, blank=True, default='', db_index=True)
    source = models.CharField(max_length=20, choices=TrafficSource.choices, default=TrafficSource.DIRECT)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='sessions')
    organization = models.CharField(max_length=150, blank=True, default='')
    network_type = models.CharField(max_length=20, choices=NetworkType.choices, default=NetworkType.UNKNOWN)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['country', '-created_at']),
            models.Index(fields=['device', '-created_at']),
        ]

    def __str__(self):
        return f"Session {self.session_id}: {self.page_count} pages ({self.total_duration}s)"


class PostAnalytics(models.Model):
    """Agregaciones diarias de analítica por post."""

    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='analytics')
    views_today = models.IntegerField(default=0)
    views_7d = models.IntegerField(default=0)
    views_30d = models.IntegerField(default=0)
    views_all_time = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0, help_text="0-100%")
    avg_scroll_depth = models.FloatField(default=0.0)
    avg_time_spent = models.IntegerField(default=0, help_text="Segundos promedio")
    unique_visitors_7d = models.IntegerField(default=0)
    trending_score = models.FloatField(default=0.0, help_text="Score para trending (7d)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Post Analytics"
        verbose_name_plural = "Post Analytics"
        ordering = ['-views_today']

    def __str__(self):
        return f"{self.post.title} → {self.views_7d} views (7d)"


class RelatedPostsCache(models.Model):
    """Cache de posts relacionados basado en tags compartidos."""

    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='related_posts_cache')
    related_posts = models.ManyToManyField(
        Post,
        related_name='related_by_cache',
        blank=True,
        help_text="Posts relacionados por tags compartidos"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Related Posts Cache"
        verbose_name_plural = "Related Posts Cache"

    def __str__(self):
        return f"Related for: {self.post.title}"


class Event(models.Model):
    """Acción relevante para la búsqueda de empleo (descarga del CV, contacto, clic en LinkedIn...)."""

    class Kind(models.TextChoices):
        CV_DOWNLOAD = 'cv_download', 'Descarga del CV'
        CONTACT_SUBMIT = 'contact_submit', 'Mensaje de contacto'
        NEWSLETTER = 'newsletter_subscribe', 'Suscripción a la newsletter'
        OUTBOUND = 'outbound_click', 'Clic a web externa'
        CASE_OPEN = 'case_open', 'Caso de éxito abierto'
        FILTER = 'filter_use', 'Filtro de proyectos'

    CONVERSIONS = (Kind.CV_DOWNLOAD, Kind.CONTACT_SUBMIT, Kind.NEWSLETTER)

    kind = models.CharField(max_length=30, choices=Kind.choices, db_index=True)
    label = models.CharField(max_length=200, blank=True, default='')
    path = models.CharField(max_length=500, blank=True, default='')
    session_id = models.CharField(max_length=100, db_index=True)
    visitor_id = models.CharField(max_length=32, blank=True, default='', db_index=True)
    asn = models.PositiveIntegerField(null=True, blank=True)
    organization = models.CharField(max_length=150, blank=True, default='')
    network_type = models.CharField(max_length=20, choices=NetworkType.choices, default=NetworkType.UNKNOWN)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='events')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        indexes = [models.Index(fields=['kind', '-timestamp'])]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} · {self.label or self.path}"
