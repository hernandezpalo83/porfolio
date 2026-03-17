from django.core.management.base import BaseCommand
from app.gym.models import Producto

class Command(BaseCommand):
    help = 'Seeds data for the gym Producto model'

    def handle(self, *args, **kwargs):
        productos = [
            {'nombre': 'Proteína Whey', 'descripcion': 'Suplemento nutricional para recuperación muscular.', 'precio': 45.99, 'stock': 100},
            {'nombre': 'Creatina Monohidrato', 'descripcion': 'Aumenta la fuerza y el rendimiento.', 'precio': 25.50, 'stock': 150},
            {'nombre': 'Mancuernas 10kg', 'descripcion': 'Par de mancuernas de acero con revestimiento.', 'precio': 60.00, 'stock': 20},
        ]
        for p_data in productos:
            Producto.objects.get_or_create(**p_data)
        self.stdout.write(self.style.SUCCESS('Successfully seeded gym products.'))
