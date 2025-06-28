# Secure Cipher Bank Backend

This is the Django backend for the Secure Cipher Bank application. It's designed to be stored in a separate repository from the frontend.

## Setup and Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the setup script to initialize the database and create a superuser:

```bash
./setup_and_run.sh
```

This will:
- Create necessary migrations
- Apply migrations to the database
- Create a superuser (admin/adminpassword)
- Start the development server

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login a user
- `POST /api/auth/logout/` - Logout a user (requires authentication)
- `POST /api/auth/update-public-key/` - Update user's public key (requires authentication)
- `POST /api/auth/set-pin/` - Mark that the user has set their PIN (requires authentication)

### User Profiles
- `GET /api/profiles/` - Get the current user's profile (requires authentication)
- `PUT /api/profiles/<id>/` - Update the current user's profile (requires authentication)

### Transactions
- `GET /api/transactions/` - List user's transactions (requires authentication)
- `GET /api/transactions/<id>/` - Get a specific transaction (requires authentication)
- `POST /api/transactions/transfer/` - Create a new transfer (requires authentication)

### Cards
- `GET /api/cards/` - List user's cards (requires authentication)
- `POST /api/cards/` - Create a new card (requires authentication)
- `GET /api/cards/<id>/` - Get a specific card (requires authentication)
- `PUT /api/cards/<id>/` - Update a card (requires authentication)
- `DELETE /api/cards/<id>/` - Delete a card (requires authentication)

### Messages
- `GET /api/messages/` - List user's messages (requires authentication)
- `GET /api/messages/<id>/` - Get a specific message (requires authentication)
- `POST /api/messages/<id>/read/` - Mark a message as read (requires authentication)

## Development

### Structure
- `api/models.py` - Contains data models (UserProfile, Transaction, Card, Message)
- `api/serializers.py` - Contains REST framework serializers for all models
- `api/views.py` - Contains all API views and ViewSets
- `api/urls.py` - URL routing for the API

### Admin Interface
The admin interface is available at `/admin/` and can be accessed with the superuser credentials.

## Production Deployment

For production deployment:

1. Update settings.py:
   - Set `DEBUG = False`
   - Configure proper `ALLOWED_HOSTS`
   - Set up a proper database (PostgreSQL recommended)
   - Configure `CORS_ALLOWED_ORIGINS` instead of `CORS_ALLOW_ALL_ORIGINS`
   - Set a proper `SECRET_KEY`

2. Set up HTTPS with a proper SSL certificate

3. Consider using Gunicorn/uWSGI with Nginx for serving the application
