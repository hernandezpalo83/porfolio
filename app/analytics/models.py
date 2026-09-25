from django.db import models
from app.blog.models import Post


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
    scroll_depth = models.IntegerField(default=0, help_text="Porcentaje scrolleado (0-100)")
    time_spent = models.IntegerField(default=0, help_text="Segundos en la página")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['path', '-timestamp']),
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['country', '-timestamp']),
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
