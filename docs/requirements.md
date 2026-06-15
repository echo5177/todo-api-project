# Requirements

## Goal

Build a small but complete Todo application for personal use, backed by a
clean REST API. The project doubles as a way to practice backend and
frontend engineering fundamentals.

## Functional requirements

### Tasks

- Create a task (title, optional description, priority, optional due date)
- List the current user's tasks, ordered usefully (unfinished first, then by
  soonest due date)
- Get a single task by id
- Update a task (partial updates)
- Delete a task
- Filter tasks by done status, priority, due date, and title
- Paginate the task list with `limit` and `offset`

### Accounts

- Register a new user
- Log in and receive a JWT access token
- Keep each user's tasks private to that user

## Non-functional requirements

- Passwords are stored only as Argon2 hashes, never in plaintext
- The JWT signing key is supplied via the `SECRET_KEY` environment variable
- Automated tests cover the task and auth flows
- Linting (ruff) and tests run in CI on every push and pull request
