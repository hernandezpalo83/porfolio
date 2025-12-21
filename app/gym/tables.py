
import django_tables2 as tables
from gym.models import Product, Producto

class ProductHTMxTable(tables.Table):
    class Meta:
        model = Product
        template_name = "tables/bootstrap_htmx.html"


class ProductoTable(tables.Table):
    class Meta:
        model = Producto
        template_name = "django_tables2/bootstrap4.html"
        fields = ("nombre", "descripcion", "precio", "stock", "fecha_creacion")
        