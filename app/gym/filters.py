# products/filters.py
from decimal import Decimal
from django.db.models import Q
import django_filters
from gym.models import Product, Producto

class ProductFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='universal_search',
                                      label="")

    class Meta:
        model = Product
        fields = ['query']

    def universal_search(self, queryset, name, value):
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return Product.objects.filter(
                Q(price=value) | Q(cost=value)
            )

        return Product.objects.filter(
            Q(name__icontains=value) | Q(category__icontains=value)
        )

class ProductoFilter(django_filters.FilterSet):
    
    nombre = django_filters.CharFilter(lookup_expr='icontains', label='Nombre')
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte', label='Precio mínimo')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte', label='Precio máximo')

    class Meta:
        model = Producto
        fields = ['nombre', 'precio_min', 'precio_max']
        