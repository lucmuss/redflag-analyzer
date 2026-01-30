#!/usr/bin/env python
"""
Script to create superuser if not exists.
"""
import os

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redflag_project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(email=email).exists():
    user = User.objects.create_superuser(
        username=email.split('@')[0],
        email=email,
        password=password
    )
    print(f'Superuser {email} created')
else:
    print(f'Superuser {email} already exists')