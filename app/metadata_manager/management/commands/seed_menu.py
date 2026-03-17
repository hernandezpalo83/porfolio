from django.core.management.base import BaseCommand
from app.landing.models import MenuItem


class Command(BaseCommand):
    help = 'Restores essential menu items to the private sidebar'

    def handle(self, *args, **kwargs):
        menu_data = [
            {
                'app_name': 'landing',
                'url_name': 'private_area',
                'title': 'Dashboard',
                'icon': 'bi bi-grid-fill',
                'order': 1,
            },
            {
                'app_name': 'prompts',
                'url_name': 'prompt_library',
                'title': 'Biblioteca de Prompts',
                'icon': 'bi bi-chat-quote-fill',
                'order': 10,
            },
            {
                'app_name': 'metadata',
                'url_name': 'metadata-demo',
                'title': 'Grid Manager',
                'icon': 'bi bi-table',
                'order': 100,
            },
        ]

        for item_data in menu_data:
            item, created = MenuItem.objects.get_or_create(
                app_name=item_data['app_name'],
                url_name=item_data['url_name'],
                defaults={
                    'title': item_data['title'],
                    'icon': item_data['icon'],
                    'order': item_data['order'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Opción '{item_data['title']}' añadida."))
            else:
                MenuItem.objects.filter(id=item.id).update(order=item_data['order'])
                self.stdout.write(self.style.WARNING(f"⚠️  La opción '{item_data['title']}' ya existía (orden actualizado)."))
