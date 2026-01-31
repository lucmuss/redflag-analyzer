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
python create_superuser.py

# Check if seed data reset is enabled
echo "DEBUG: SEED_DATA_RESET_ON_START=$SEED_DATA_RESET_ON_START"
if [ "$SEED_DATA_RESET_ON_START" = "true" ]; then
    echo "🔄 SEED_DATA_RESET_ON_START is true - clearing existing data before seeding..."
    python clear_seed_data.py
fi

echo "Seeding questions..."
if python manage.py seed_questions; then
    echo "Questions seeded successfully"

    if [ -f "../seed_data/users.json" ]; then
        echo "Seeding test users..."
        python manage.py seed_test_users || echo "Warning: Test user seeding failed, continuing..."
    else
        echo "Skipping test user seeding (seed data not available)"
    fi
else
    echo "Warning: Question seeding failed - skipping user seeding"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>&1 || echo "Static collection failed, continuing..."

echo "Starting server..."
echo "Running: $@"
exec "$@" 2>&1
