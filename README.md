# My Todo API

A simple Todo API project built with FastAPI.

## Run

```bash
fastapi dev main.py
```

API Docs
--------

Open in browser:

[My Todo API - Swagger UI](http://127.0.0.1:8000/docs)

Features
--------

* Create a task

* List tasks

* Get one task by id

* Update a task

* Delete a task

* Filter tasks by done status

Database
--------

This project uses SQLite with SQLModel.

## Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run tests

```bash
python -m pytest
```

## Lint and format

```bash
ruff check .
ruff format .
```

## Current Features

- Create a task
- List tasks
- Get one task by id
- Update a task
- Delete a task
- Filter tasks by done status
- Filter tasks by priority
- Support task priority: low / medium / high
- Support optional due date

## Frontend

### Install dependencies

```bash
cd frontend
npm install
```
### Local environment

Create a file named `.env.local` inside `frontend/`:
    NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000

### Run in development mode

    npm run dev

### Production-like local run

    npm run build
    npm run start

Backend
-------

### Example environment variables

    SECRET_KEY=replace-this-with-a-real-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

### Run backend

    fastapi dev app/main.py

Current Features
----------------

* User registration

* User login with JWT

* Current user profile

* User-specific tasks

* Create, edit, delete tasks

* Filter tasks

* Frontend pages for register, login, and tasks
  