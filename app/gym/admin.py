
from django.contrib import admin
from .models import Product, Producto

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cost', 'profit_margin', 'status')
    list_filter = ('status', 'category')
    list_editable = ('status',)
    search_fields = ('name', 'category')
    ordering = ('name',)
    readonly_fields = ('profit_margin_display',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'status')
        }),
        ('Precios', {
            'fields': ('price', 'cost', 'profit_margin_display')
        }),
    )
    
    def profit_margin(self, obj):
        """Mostrar margen de ganancia en porcentaje"""
        if obj.cost == 0:
            return "N/A"
        margin = ((obj.price - obj.cost) / obj.cost * 100)
        return f"{margin:.1f}%"
    profit_margin.short_description = "Margen"
    
    def profit_margin_display(self, obj):
        return self.profit_margin(obj)
    profit_margin_display.short_description = "Margen de Ganancia"

    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_desc_short', 'precio', 'stock', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'precio')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'precio', 'stock')
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