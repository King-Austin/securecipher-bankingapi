#!/bin/bash

# Navigate to the backend directory
cd /workspaces/codespaces-react/backend

# Make migrations for the database
echo "Making migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Create a superuser (non-interactive)
echo "Creating superuser..."
if python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists()" | grep -q "False"; then
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"
    echo "Superuser created with username: admin, password: adminpassword"
else
    echo "Superuser 'admin' already exists"
fi

# Check if we're in development or production mode
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting Django server with Gunicorn (production mode)..."
    gunicorn -c gunicorn_config.py secure_cipher_bank.wsgi:application
else
    echo "Starting Django development server..."
    python manage.py runserver 0.0.0.0:8000
fi
