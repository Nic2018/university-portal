# Multi-User Login System

A complete web-based login system for multiple users built with **HTML**, **Python (Django)**, and (optionally) **MySQL**.

## Features

- ✅ User registration and login
- ✅ Secure password hashing with bcrypt
- ✅ MySQL database for user storage (compatible with MySQL Workbench!)
- ✅ Session management
- ✅ Modern, responsive UI
- ✅ Flash messages for user feedback
- ✅ Protected dashboard page

## Project Structure

```
cse/
├── manage.py
├── login_system/          # Django project package (settings, urls, wsgi)
├── accounts/              # App providing registration/login/dashboard
├── templates/             # Django templates used by the `accounts` app
│   ├── index.html
│   ├── register.html
│   ├── dashboard.html
│   └── admin_users.html
├── requirements.txt
├── db.sqlite3             # Created after running migrations (ignored by git)
└── README.md
```

## Quick Start

### Quick Start (Django)

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run migrations and create a superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

3. Run the development server:

```powershell
python manage.py runserver 8000
```

4. Open your browser and go to `http://localhost:8000`.

Notes:
- The project uses SQLite by default (no DB server required). If you prefer MySQL, install a MySQL driver (e.g. `mysqlclient`) and update `login_system/settings.py` DATABASES accordingly.

## Sample Accounts

There are no pre-seeded sample accounts in this Django scaffold. Create a superuser with `python manage.py createsuperuser` or add users via the admin interface at `/admin/`.

## How It Works

### Database

This scaffold uses Django's built-in `auth` user model and the default migration-created tables. Passwords are stored using Django's secure password hashing (PBKDF2 by default). To use MySQL in production, update `DATABASES` in `login_system/settings.py` and install a compatible DB driver.


### Authentication Flow

1. **Registration:** Users create accounts via `/register`.
   - Username must be unique.
   - Passwords are hashed by Django when saved.

2. **Login:** Users sign in at `/login`.
   - Django's `authenticate()` verifies credentials.
   - A session is created on successful login.

3. **Dashboard:** Protected page at `/dashboard`.
   - Requires an authenticated user.

4. **Logout:** Clears session and redirects to login.

## Security Features

- ✅ Password hashing with bcrypt (industry standard)
- ✅ Session-based authentication
- ✅ SQL injection protection (parameterized queries)
- ✅ Input validation and sanitization
- ✅ Flash messages for user feedback

## Development Notes

- The Flask app (`app.py`) automatically creates the database on first run
- Use `init_db.py` to add sample users or reset the database
- For production use, consider:
  - HTTPS/SSL certificates
  - Environment variables for secrets
  - Rate limiting
  - CSRF protection
  - Password strength requirements

## Technologies Used

- **Backend:** Python 3, Django
- **Database:** SQLite (default), MySQL optional
- **Security:** Django's built-in password hashing and authentication
- **Frontend:** HTML5, CSS3
- **Templating:** Django templates (Jinja-like syntax)
