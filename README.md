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
