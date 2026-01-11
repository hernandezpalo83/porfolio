from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
import math

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
        null=True, 
        help_text="Pega aquí la URL 'raw' de GitHub"
    )

    class Meta:
        ordering = ('-publish',)



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

    
    def get_read_time(self):
        try:
            from django.utils.html import strip_tags
            if not self.content:
                return 1
            #texto_limpio = strip_tags(self.content)
            #conteo_palabras = len(texto_limpio.split())
            #return max(1, math.ceil(conteo_palabras / 200))
            return 6
        except Exception:
            return 1 # Fallback seguro para que la web no se cuelgue