
from django.contrib import admin
from .models import Product, Producto

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'cost', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name', 'category')
    ordering = ('name',)
    
    
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'stock', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)