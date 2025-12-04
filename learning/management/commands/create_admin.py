"""
Management command to create an admin user
Run with: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from learning.models import AdminProfile


class Command(BaseCommand):
    help = 'Creates an admin user with AdminProfile'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for admin')
        parser.add_argument('--email', type=str, help='Email for admin')
        parser.add_argument('--password', type=str, help='Password for admin')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')

        if not username:
            username = input('Enter username: ')
        if not email:
            email = input('Enter email: ')
        if not password:
            password = input('Enter password: ')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))
            # Ensure user has staff privileges for Django admin access
            if not user.is_staff:
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Granted staff privileges to {username}'))
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

        # Create or get admin profile
        admin_profile, created = AdminProfile.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created admin profile for {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin profile already exists for {username}'))
        
        # Ensure user has staff privileges (required for Django admin access)
        if not user.is_staff:
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Granted staff privileges to {username}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nAdmin user "{username}" is ready!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Login at: /admin/login/')
        )

