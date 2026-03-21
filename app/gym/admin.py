
from django.contrib import admin
from .models import Producto
    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_desc_short', 'precio', 'coste', 'stock', 'estado', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'precio', 'estado')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'precio', 'coste', 'stock', 'estado')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_desc_short(self, obj):
        """Mostrar descripción corta"""
        desc = obj.descripcion if obj.descripcion else ""
        return desc[:50] + "..." if len(desc) > 50 else desc
    get_desc_short.short_description = "Descripción"