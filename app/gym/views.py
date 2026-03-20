from django.shortcuts import render
from django_tables2 import RequestConfig
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.http import HttpRequest, HttpResponse
from typing import Any

from app.gym.models import Product, Producto
from app.gym.tables import ProductHTMxTable, ProductoTable
from app.gym.filters import ProductFilter, ProductoFilter

class ProductHTMxTableView(SingleTableMixin, FilterView):
    table_class = ProductHTMxTable
    queryset = Product.objects.all().order_by("name")
    filterset_class = ProductFilter
    paginate_by = 15

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            template_name = "product_table_partial.html"
        else:
            template_name = "product_table_htmx.html"
        return [template_name]

def lista_productos(request: HttpRequest) -> HttpResponse:
    queryset = Producto.objects.all()
    producto_filter = ProductoFilter(request.GET, queryset=queryset)
    table = ProductoTable(producto_filter.qs)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)

    if request.htmx:
        return render(request, "productos/tabla_parcial.html", {"table": table})

    return render(request, "productos/lista_productos.html", {
        "table": table,
        "filter": producto_filter
    })

def mantenimiento_productos(request: HttpRequest) -> HttpResponse:
    """
    Vista de mantenimiento para el modelo Producto usando comp_tabla_mantenimiento.
    """
    columnas = [
        {"title": "ID", "field": "id", "width": 70, "editor": False},
        {"title": "Nombre", "field": "nombre", "headerFilter": "input"},
        {"title": "Precio", "field": "precio", "hozAlign": "right", "formatter": "money", "formatterParams": {"symbol": "$"}},
        {"title": "Stock", "field": "stock", "hozAlign": "center", "editor": "number"},
        {"title": "Descripción", "field": "descripcion", "width": 300},
        {"title": "Fecha", "field": "fecha_creacion", "formatter": "datetime", "editor": False, 
         "formatterParams": {"inputFormat": "iso", "outputFormat": "dd/MM/yyyy HH:mm"}},
    ]
    
    return render(request, "gym/mantenimiento_generico.html", {
        "titulo": "Mantenimiento de Productos",
        "descripcion": "Gestión completa de inventario de productos.",
        "cols": columnas,
        "api_url": "/gym/api/productos-api/"
    })