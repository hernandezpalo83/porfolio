
from django.db import models
from django.core.exceptions import ValidationError



class Producto(models.Model):
    class Estado(models.IntegerChoices):
        ACTIVE = 1, "Active"
        INACTIVE = 2, "Inactive"
        ARCHIVED = 3, "Archived"

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    coste = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField()
    estado = models.PositiveSmallIntegerField(choices=Estado.choices, default=Estado.ACTIVE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


    def clean(self):
        """Validar que price >= coste"""
        if self.precio < self.coste:
            raise ValidationError("El precio no puede ser menor al costo")

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Productos"
