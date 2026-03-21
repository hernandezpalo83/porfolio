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
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

    def clean(self):
        """Validar datos de negocio del producto."""
        errors = {}
        if self.precio is not None and self.precio < 0:
            errors['precio'] = "El precio no puede ser negativo."
        if self.coste is not None and self.coste < 0:
            errors['coste'] = "El coste no puede ser negativo."
        if self.precio is not None and self.coste is not None and self.precio < self.coste:
            errors['precio'] = "El precio no puede ser menor al costo."
        if errors:
            raise ValidationError(errors)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['-fecha_creacion']),
        ]
