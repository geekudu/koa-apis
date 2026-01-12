# KOA Django API

Django REST API backend for managing KOA members with authentication.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (required for admin portal access):
```bash
python manage.py createsuperuser
```

4. Start the development server:
```bash
python manage.py runserver
```

The API will be available at:
- API: http://localhost:8000/api/members/
- Django Admin: http://localhost:8000/admin/

## Authentication

The API uses Django's session authentication. All endpoints (except login) require authentication.

**Important**: Only Django superusers can access the admin portal. Make sure to create a superuser account.

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login with username and password (requires superuser)
- `POST /api/auth/logout/` - Logout (requires authentication)
- `GET /api/auth/check/` - Check authentication status (requires authentication)

### Members (all require authentication)
- `GET /api/members/` - List all members
- `POST /api/members/` - Create a new member
- `GET /api/members/{id}/` - Get a specific member
- `PUT /api/members/{id}/` - Update a member
- `PATCH /api/members/{id}/` - Partially update a member
- `DELETE /api/members/{id}/` - Delete a member

## CORS Configuration

CORS is configured to allow requests from:
- http://localhost:3000
- http://127.0.0.1:3000

This allows the React admin portal to communicate with the Django API. Credentials are enabled for session-based authentication.

