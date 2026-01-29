#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
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
END

echo "Seeding questions..."
python manage.py seed_questions || echo "Warning: Seeding failed, continuing..."

if [ -f "users.json" ]; then
    echo "Seeding test users..."
    python manage.py seed_test_users || echo "Warning: Test user seeding failed, continuing..."
else
    echo "Skipping test user seeding (seed data not available)"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
