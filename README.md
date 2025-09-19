# Trucking Management Backend

A Django REST API backend for managing trucking operations, including drivers, vehicles, trips, logs, locations, and compliance reports.

## Project Structure

```
.env
.gitignore
manage.py
README.md
.qodo/
apps/
    drivers/
    locations/
    logs/
    reports/
    trips/
    users/
    utils/
    vehicles/
env/
trucking/
    __init__.py
    asgi.py
    urls.py
    wsgi.py
    settings/
```

## Features

- **User Authentication**: JWT-based registration and login ([`apps/users/api/views.py`](apps/users/api/views.py))
- **Driver Management**: CRUD for drivers ([`apps/drivers/api/views.py`](apps/drivers/api/views.py))
- **Vehicle Management**: CRUD for vehicles and location tracking ([`apps/vehicles/api/views.py`](apps/vehicles/api/views.py))
- **Trip Management**: Plan, update, and track trips ([`apps/trips/api/views.py`](apps/trips/api/views.py))
- **Location Services**: Save and list locations ([`apps/locations/api/views.py`](apps/locations/api/views.py))
- **HOS Logs**: Manage Hours of Service logs and violations ([`apps/logs/api/views.py`](apps/logs/api/views.py))
- **Compliance Reports**: Fleet and driver compliance summaries ([`apps/reports/api/views.py`](apps/reports/api/views.py))
- **Admin Interface**: Custom admin for all models

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```sh
   python -m venv env
   source env/bin/activate  # or .\env\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   - Copy `.env.example` to `.env` and update values as needed.

4. **Apply migrations**
   ```sh
   python manage.py migrate
   ```

5. **Run the development server**
   ```sh
   python manage.py runserver
   ```

## API Endpoints

- `/api/auth/` – User registration and login
- `/api/drivers/` – Driver management
- `/api/vehicles/` – Vehicle management and location history
- `/api/trips/` – Trip management
- `/api/locations/` – Location management
- `/api/logs/` – HOS logs and violations
- `/api/reports/` – Compliance reports

Interactive API docs available at:
- `/api/swagger/` (Swagger UI)
- `/api/redoc/` (ReDoc)

## Admin Panel

Access the Django admin at `/admin/` with superuser credentials.

## License

See [LICENSE](LICENSE) for details.

---

For more details, see the code in the respective `apps/` subfolders.