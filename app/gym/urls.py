from django.urls import path
from .views import ProductHTMxTableView, lista_productos

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('products/', ProductHTMxTableView.as_view(), name='product_list'),
]