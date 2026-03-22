import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from django.utils.text import Truncator

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    
    # Usamos CKEditor 5 para el cuerpo del post
    content = CKEditor5Field('Content', config_name='default')
    excerpt = models.TextField(blank=True, help_text="Resumen automático para el listado")
    
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # SEO Meta Tags específicos por post
    meta_description = models.CharField(max_length=160, blank=True, help_text="Para Google Snippet")
    imagen_url = models.URLField(
        max_length=500, 
        blank=True, 
        default='',
        help_text="Pega aquí la URL 'raw' de GitHub"
    )

    class Meta:
        ordering = ('-publish',)
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        indexes = [
            models.Index(fields=['status', '-publish']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        # Si el excerpt está vacío, lo generamos del contenido
        if not self.excerpt and self.content:
            # Quitamos etiquetas HTML y cortamos a 250 caracteres
            texto_plano = strip_tags(self.content)
            self.excerpt = Truncator(texto_plano).chars(250)
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    
    def get_read_time(self) -> int:
        """Calcula el tiempo de lectura estimado a 200 palabras/minuto."""
        try:
            if not self.content:
                return 1
            texto_plano = strip_tags(self.content)
            palabras = len(texto_plano.split())
            return max(1, round(palabras / 200))
        except Exception:
            return 1


# ── NEW-003: Newsletter ───────────────────────────────────────────────────────

class Subscriber(models.Model):
    """Suscriptor al newsletter del blog con double opt-in."""

    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-subscribed_at',)
        verbose_name = "Suscriptor"
        verbose_name_plural = "Suscriptores"

    def __str__(self):
        status = "✓" if self.confirmed else "⏳"
        return f"{status} {self.email}"

    def get_confirm_url(self):
        return reverse('blog:confirm_subscription', args=[str(self.token)])