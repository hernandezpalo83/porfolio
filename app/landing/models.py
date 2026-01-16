from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

class Info(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    perfil = models.TextField(null=True, blank=True)
    skill = models.TextField(null=True, blank=True)
    resumen = models.TextField(null=True, blank=True)
    web = models.CharField(max_length=100,null=True, blank=True)
    nacimiento = models.CharField(max_length=100, default='8 de Noviembre de 1983')
    trabajo = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/')
    porfolio_title = models.CharField(max_length=150, default='Portfolio')
    porfolio_subtitle = models.CharField(max_length=300, default='Portfolio')
    porfolio_description = models.TextField(null=True, blank=True)
    Experience_title = models.CharField(max_length=150, default='Experience')
    Experience_subtitle = models.CharField(max_length=300, default='Experience')
    Experience_description = CKEditor5Field('Text', config_name='default', blank=True, null=True, default="")
    
class Skill(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField(default= 90)
    
class Experience(models.Model):
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    resumen = CKEditor5Field('Text', config_name='default', blank=True, null=True, default="")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

class Education(models.Model):
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    resumen = CKEditor5Field('Text', config_name='default', blank=True, null=True, default="")
    link = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = CKEditor5Field('Text', config_name='default', blank=True, null=True, default="")
    imagen = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    link = models.TextField(null=True, blank=True)

class Contact(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    
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
    url_name = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='submenus')
    order = models.IntegerField(default=0)
    groups = models.ManyToManyField(Group, blank=True, help_text="Grupos que pueden ver esta opción")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']