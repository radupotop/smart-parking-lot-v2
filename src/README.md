# Smart Parking Lot

This directory is the Python project root for the Django REST Framework
application.

## Virtual environment

Run the environment bootstrap command from this directory:

```bash
uv venv --seed --clear --no-managed-python
```

The command creates a local `.venv/` using an already-installed Python 3.14
interpreter rather than a uv-managed Python installation.

## Tests

Run the project test suite from this directory:

```bash
uv run python manage.py test
```

## Podman runtime

### Compose workflow

From the repository root, build and start the Django development server with
Podman Compose:

```bash
podman compose up --build
```

The compose service builds from the root `Containerfile`, publishes the Django
development server on <http://localhost:8000>, sets
`DJANGO_SQLITE_PATH=/app/data/db.sqlite3`, and mounts root `data/` to
`/app/data` so SQLite data persists outside the container.

Run migrations against the mounted database through the one-off test/manage
service:

```bash
podman compose run --rm test uv run python manage.py migrate
```

Run tests through the dedicated test service:

```bash
podman compose run --rm test
```

Run other Django management commands from the same container shape:

```bash
podman compose run --rm test uv run python manage.py check
```

Stop the development server with `Ctrl+C`, or from another shell:

```bash
podman compose down
```

### Single-container commands

The compose services replace the manual `podman run ... uv run python
manage.py ...` commands. Build the image directly only when you need to inspect
the image outside the compose workflow:

```bash
podman build -t smart-parking-lot -f Containerfile .
```
