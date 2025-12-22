"""
Management command to load data from a JSON file via remote server
"""
import json
import os
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from django.db import transaction

class Command(BaseCommand):
    help = 'Load data from JSON file exported via dumpdata'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file to load')
        parser.add_argument('--flush', action='store_true', help='Flush database first')

    def handle(self, *args, **options):
        json_file = options['json_file']
        flush = options.get('flush', False)

        # Verify file exists
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f'File not found: {json_file}')
            )
            return

        file_size = os.path.getsize(json_file)
        self.stdout.write(f'Loading from: {json_file} ({file_size} bytes)')

        # Load data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Count objects
            self.stdout.write(f'Total objects in file: {len(json_data)}')

            # Load using deserialize
            with transaction.atomic():
                object_count = 0
                for obj in deserialize('json', json.dumps(json_data)):
                    obj.save()
                    object_count += 1
                    if object_count % 10 == 0:
                        self.stdout.write(f'  Loaded {object_count} objects...')

            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully loaded {object_count} objects')
            )

            # Show summary
            from app.landing.models import Skill, Experience, Education, Project, Info, Contact
            from app.gym.models import Producto

            self.stdout.write('\nData Summary:')
            self.stdout.write(f'  Skills: {Skill.objects.count()}')
            self.stdout.write(f'  Experience: {Experience.objects.count()}')
            self.stdout.write(f'  Education: {Education.objects.count()}')
            self.stdout.write(f'  Projects: {Project.objects.count()}')
            self.stdout.write(f'  Contacts: {Contact.objects.count()}')
            self.stdout.write(f'  Info: {Info.objects.count()}')
            self.stdout.write(f'  Productos: {Producto.objects.count()}')

        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading data: {e}')
            )
            import traceback
            traceback.print_exc()
