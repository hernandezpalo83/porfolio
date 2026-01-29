from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Verifies all critical URLs in the project by sending GET requests'

    def handle(self, *args, **options):
        # Patch ALLOWED_HOSTS to include testserver for the test client
        from django.conf import settings
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

        self.stdout.write(self.style.WARNING("Starting URL verification..."))
        
        client = Client()
        
        # 1. Test Key URLs (Smoke Test)
        # We simulate an admin user to test private routes too
        User = get_user_model()
        username = 'admin_test_verify'
        
        # Cleanup previous run if crashed
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            
        admin_user = User.objects.create_superuser(username, 'admin@example.com', 'testpass123')
        client.force_login(admin_user)
        
        critical_paths = [
            '/', 
            '/private/', 
            '/prompts/', 
            '/blog/',
            '/gym/productos/',
            '/login/'
        ]
        
        errors = []
        
        self.stdout.write(self.style.WARNING("\nChecking CRITICAL paths..."))
        for path in critical_paths:
            try:
                resp = client.get(path, follow=True)
                if resp.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"OK: {path}"))
                else:
                    self.stdout.write(self.style.ERROR(f"FAIL: {path} returned {resp.status_code}"))
                    errors.append(f"{path} returned {resp.status_code}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"FAIL: {path} Exception {e}"))
                errors.append(f"{path} exception: {e}")

        # Cleanup
        admin_user.delete()

        if errors:
            self.stdout.write(self.style.ERROR(f"\nFound {len(errors)} errors!"))
            import sys
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS("\nAll critical URLs passed successfully!"))
