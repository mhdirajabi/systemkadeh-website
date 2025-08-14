#!/bin/sh

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database ready!"

# Run migrations
python manage.py makemigrations
python manage.py migrate

exec "$@"