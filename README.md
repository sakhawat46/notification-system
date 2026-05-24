# Notification System

Backend API for scheduling notifications with Django REST Framework, Celery, Redis, and PostgreSQL.

## Features

- JWT-based user authentication
- Create and schedule notifications
- Notification history per user
- Retry failed notifications manually
- Reject past scheduled times
- Permanent failure after 3 failed delivery attempts
- Docker Compose setup for Django, PostgreSQL, Redis, and Celery worker
- Structured logging for Django, Celery, and notification jobs

## API Endpoints

- `POST /api/v1/signup/`
- `POST /api/v1/login/`
- `POST /api/v1/logout/`
- `GET /api/v1/notifications/`
- `POST /api/v1/notifications/`
- `GET /api/v1/notifications/<uuid:notification_id>/`
- `POST /api/v1/notifications/<uuid:notification_id>/retry/`

## Notification Rules

- `scheduled_time` must be in the future.
- A failed delivery increments `retry_count`.
- When `retry_count` reaches `3`, the notification becomes `PERMANENTLY_FAILED`.
- Retry endpoint only accepts notifications in `FAILED` state.

## Local Run

1. Create an env file from `.env.example`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start Django:

```bash
python manage.py runserver
```

5. Start Celery worker:

```bash
celery -A projects worker --loglevel=info --pool=solo
```

If you want PostgreSQL locally, set the `POSTGRES_*` variables. Without them, the project falls back to SQLite for quick local development.

## Docker Run

```bash
docker compose up --build
```

Services:

- Django API: `http://127.0.0.1:8000`
- PostgreSQL: `127.0.0.1:5432`
- Redis: `127.0.0.1:6379`

## Test

```bash
python manage.py test
```
