from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

class Info(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    perfil = models.TextField(blank=True, default='')
    skill = models.TextField(blank=True, default='')
    resumen = models.TextField(blank=True, default='')
    web = models.CharField(max_length=100, blank=True, default='')
    nacimiento = models.CharField(max_length=100, default='8 de Noviembre de 1983')
    trabajo = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/')
    porfolio_title = models.CharField(max_length=150, default='Portfolio')
    porfolio_subtitle = models.CharField(max_length=300, default='Portfolio')
    porfolio_description = models.TextField(blank=True, default='')
    Experience_title = models.CharField(max_length=150, default='Experience')
    Experience_subtitle = models.CharField(max_length=300, default='Experience')
    Experience_description = CKEditor5Field('Text', config_name='default', blank=True, default="")
    
    def __str__(self):
        return self.name
    
class Skill(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=90)
    
    def __str__(self):
        return f"{self.name} ({self.score}%)"
    
    def clean(self):
        """Validar que score esté entre 0 y 100"""
        if not 0 <= self.score <= 100:
            raise ValidationError("Score debe estar entre 0 y 100")
    
class Experience(models.Model):
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    resumen = CKEditor5Field('Text', config_name='default', blank=True, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.position} @ {self.company}"
    
    def clean(self):
        """Validar que end_date > start_date si está presente"""
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("La fecha de fin no puede ser anterior a la de inicio")

class Education(models.Model):
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    resumen = CKEditor5Field('Text', config_name='default', blank=True, default="")
    link = models.TextField(blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.degree} @ {self.institution}"
    
    def clean(self):
        """Validar que end_date > start_date"""
        if self.end_date < self.start_date:
            raise ValidationError("La fecha de fin no puede ser anterior a la de inicio")

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = CKEditor5Field('Text', config_name='default', blank=True, default="")
    imagen = models.TextField(blank=True, default='')
    categoria = models.CharField(max_length=100, blank=True, default='')
    link = models.TextField(blank=True, default='')

    def __str__(self):
        return self.title

class Contact(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    def __str__(self):
        return self.email
    
    
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)  # Para tu gestión interna

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
    
class MenuItem(models.Model):
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Clase de FontAwesome o Bootstrap Icons")
    app_name = models.CharField(max_length=50, default='landing', help_text="Ej: landing, prompts, blog")
    url_name = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='submenus')
    order = models.IntegerField(default=0)
    groups = models.ManyToManyField(Group, blank=True, help_text="Grupos que pueden ver esta opción")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Metric(models.Model):
    """Métricas de impacto para la landing page"""
    value = models.IntegerField(help_text="Valor numérico del contador (ej: 25, 100)")
    prefix = models.CharField(max_length=10, blank=True, default='', help_text="Prefijo opcional (ej: '+')")
    suffix = models.CharField(max_length=10, blank=True, default='', help_text="Sufijo opcional (ej: '%')")
    title = models.CharField(max_length=100, help_text="Título de la métrica")
    description = models.TextField(help_text="Descripción detallada")
    is_visible = models.BooleanField(default=True, verbose_name="Visible")
    order = models.IntegerField(default=0, help_text="Orden de aparición (menor = primero)")
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Métrica de Impacto"
        verbose_name_plural = "Métricas de Impacto"
    
    def __str__(self):
        return f"{self.prefix}{self.value}{self.suffix} - {self.title}"
    
    def get_percent(self):
        """Calcula el porcentaje para el círculo de progreso (máximo 100)"""
        return min(self.value, 100)