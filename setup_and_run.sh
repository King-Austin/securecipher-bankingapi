#!/bin/bash

# Navigate to the backend directory
# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python first."
    exit 1
fi

# Navigate to the project root
cd "$(dirname "$0")"

# Create and activate virtual environment
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment (works for both Windows and Unix-like systems)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt


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
