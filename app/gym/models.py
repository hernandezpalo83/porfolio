
from django.db import models
from django.core.exceptions import ValidationError

class Product(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 1, "Active"
        INACTIVE = 2, "Inactive"
        ARCHIVED = 3, "Archived"

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=Status.choices)

    def __str__(self):
        return f"{self.name} (${self.price})"
    
    def clean(self):
        """Validar que price >= cost"""
        if self.price < self.cost:
            raise ValidationError("El precio no puede ser menor al costo")

    class Meta:
        ordering = ['name']


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = "Productos"

