# My Todo

A small but complete personal Todo app: a FastAPI + SQLModel backend with a
Next.js (React) frontend. Each user signs in and manages their own private
list of tasks.

## Features

- Register and log in (JWT-based auth, Argon2 password hashing)
- Each user only ever sees their own tasks
- Create, read, update, and delete tasks
- Task fields: title, description, priority (low / medium / high), optional
  due date, and `created_at` / `updated_at` timestamps
- Filter by done status, priority, due date, and title
- Pagination with `limit` and `offset`
- Tasks are returned in a useful order (unfinished first, soonest due date
  first, undated last) and the frontend flags overdue tasks

## Tech stack

| Layer    | Tech                                  |
| -------- | ------------------------------------- |
| Backend  | FastAPI, SQLModel, SQLite, PyJWT      |
| Frontend | Next.js, React, TypeScript, Tailwind  |
| Tooling  | pytest, ruff, ESLint, GitHub Actions  |

## Backend

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure environment

Copy the example file and set a real secret key:

```bash
cp backend.env.example .env
# Generate a strong key, e.g.:
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

If `SECRET_KEY` is not set the app generates a temporary in-memory key and
warns loudly — fine for a quick local run, not for anything you keep.

### Run

```bash
fastapi dev app/main.py
```

API docs (Swagger UI): http://127.0.0.1:8000/docs

### Test, lint, format

```bash
python -m pytest
ruff check .
ruff format .
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the API base URL from `NEXT_PUBLIC_API_BASE_URL`
(defaults to `http://127.0.0.1:8000`).

## Database

SQLite via SQLModel. Tables are created automatically on startup; the
database file is local and git-ignored.
