from django.shortcuts import render
from django_tables2 import RequestConfig
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView
from django.http import HttpRequest, HttpResponse
from typing import Any

from app.gym.models import Producto

def mantenimiento_productos(request: HttpRequest) -> HttpResponse:
    """
    Vista de mantenimiento para el modelo Producto usando comp_tabla_mantenimiento.
    """
    columnas = [
        {"title": "ID", "field": "id", "width": 70, "editor": False},
        {"title": "Nombre", "field": "nombre", "headerFilter": "input"},
        {"title": "Precio", "field": "precio", "hozAlign": "right", "formatter": "money", "formatterParams": {"symbol": "$"}},
        {"title": "Stock", "field": "stock", "hozAlign": "center", "editor": "number"},
        {"title": "Coste", "field": "coste", "hozAlign": "center", "editor": "number"},
        {"title": "Descripción", "field": "descripcion", "width": 300},
        {"title": "Estado", "field": "estado", "hozAlign": "center", "editor": "select", "editorParams": {"values": {"1": "Active", "2": "Inactive", "3": "Archived"}}},
        {"title": "Fecha", "field": "fecha_creacion", "formatter": "datetime", "editor": False, 
         "formatterParams": {"inputFormat": "iso", "outputFormat": "dd/MM/yyyy HH:mm"}},
    ]
    
    return render(request, "gym/mantenimiento_generico.html", {
        "titulo": "Mantenimiento de Productos",
        "descripcion": "Gestión completa de inventario de productos.",
        "cols": columnas,
        "api_url": "/gym/api/productos/"
    })