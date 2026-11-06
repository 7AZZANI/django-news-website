#!/bin/bash
set -e

# Default settings module if unset
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-news_project.settings.prod}

echo "=================================================="
echo "📰 The Chronicle News Platform — Container Startup"
echo "Active Settings: ${DJANGO_SETTINGS_MODULE}"
echo "=================================================="

# Wait for PostgreSQL database if configured
if [ "$DB_ENGINE" = "django.db.backends.postgresql" ] || [ -n "$DB_HOST" ]; then
    DB_HOST_CHECK=${DB_HOST:-db}
    DB_PORT_CHECK=${DB_PORT:-5432}
    echo "Waiting for PostgreSQL at ${DB_HOST_CHECK}:${DB_PORT_CHECK}..."
    while ! nc -z "$DB_HOST_CHECK" "$DB_PORT_CHECK"; do
        sleep 0.5
    done
    echo "PostgreSQL is reachable and accepting connections!"
fi

# Wait for Redis cache if configured
if [ -n "$REDIS_HOST" ]; then
    REDIS_HOST_CHECK=${REDIS_HOST:-redis}
    REDIS_PORT_CHECK=${REDIS_PORT:-6379}
    echo "Waiting for Redis at ${REDIS_HOST_CHECK}:${REDIS_PORT_CHECK}..."
    while ! nc -z "$REDIS_HOST_CHECK" "$REDIS_PORT_CHECK"; do
        sleep 0.5
    done
    echo "Redis is reachable!"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static assets
echo "Collecting static assets..."
python manage.py collectstatic --noinput

# Optionally seed news dataset if requested
if [ "$SEED_DEMO_DATA" = "True" ] || [ "$SEED_DEMO_DATA" = "true" ] || [ "$SEED_DEMO_DATA" = "1" ]; then
    echo "Seeding editorial demo articles, categories, and accounts..."
    python manage.py seed_news || echo "Seed data already initialized or skipped."
fi

echo "Startup initialization complete. Launching server..."
exec "$@"
