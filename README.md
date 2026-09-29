# Smart Parking Lot

A Django REST Framework billing engine for a smart, multi-level parking
complex. Tickets are issued as open `ParkingSession`s on entry; on exit the
rate calculator evaluates every pricing policy (Standard Hourly with weekday
peak surcharge, Early Bird, Night Owl), persists one auditable
`RateEvaluation` per policy, and charges the customer the lowest valid fare.
See `specs/` for the PRD/SRS/ERD documents and `backlog/` for the task
history.

## Required tools

- **Python 3.14** and **uv** — for running the project directly.
- **Podman** (with `podman compose`) — for the containerized runtime.
- **Node.js / npm** — only if you want the `backlog` CLI (see below).

## Running with Podman

From the repository root:

```bash
# Build and start the Django dev server (http://localhost:8000)
podman compose up --build

# Run migrations against the mounted SQLite database
podman compose run --rm migrate

# Run the test suite
podman compose run --rm test
```

The compose file mounts `./data/` into the container and sets
`DJANGO_SQLITE_PATH=/app/data/db.sqlite3`, so the database persists on the
host filesystem. Stop everything with `podman compose down`.

## Running manually with uv

From the `src/` directory:

```bash
# Install dependencies into .venv/
uv sync

# Apply migrations
uv run python manage.py migrate

# Start the dev server (http://localhost:8000)
uv run python manage.py runserver

# Run the test suite
uv run python manage.py test
```

The SQLite database file defaults to `src/db.sqlite3`; override the location
with the `DJANGO_SQLITE_PATH` environment variable.

## Backlog

Project tasks are tracked in `backlog/` with the
[Backlog.md](https://github.com/MrLesk/Backlog.md) tool. Install the CLI to
view and manage the backlog:

```bash
npm i -g backlog.md
```

Then, from the repository root:

```bash
backlog task list   # list all tasks
backlog board       # open the kanban board
```
