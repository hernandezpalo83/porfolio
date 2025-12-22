from django.shortcuts import render
from django_tables2 import RequestConfig
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView

from app.gym.models import Product, Producto
from app.gym.tables import ProductHTMxTable, ProductoTable
from app.gym.filters import ProductFilter, ProductoFilter

class ProductHTMxTableView(SingleTableMixin, FilterView):
    table_class = ProductHTMxTable
    queryset = Product.objects.all()
    filterset_class = ProductFilter
    paginate_by = 15

    def get_template_names(self):
        if self.request.htmx:
            template_name = "product_table_partial.html"
        else:
            template_name = "product_table_htmx.html"
        return template_name

def lista_productos(request):
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