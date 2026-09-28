# Smart Parking Lot

This directory is the Python project root for the Django REST Framework
application.

## Virtual environment

Run the environment bootstrap command from this directory:

```bash
uv venv --seed --clear --no-managed-python
```

The command creates a local `.venv/` using an already-installed Python
interpreter rather than a uv-managed Python installation.

## Tests

Run the project test suite from this directory:

```bash
uv run python manage.py test
```

## Podman runtime

Build the development image from the repository root:

```bash
podman build -t smart-parking-lot -f Containerfile .
```

The container uses `/app/data/db.sqlite3` by default. Mount a host directory
there so SQLite data persists outside the container:

```bash
mkdir -p data
podman run --rm -it \
  -p 8000:8000 \
  -v ./data:/app/data:Z \
  smart-parking-lot
```

Run migrations against the mounted database:

```bash
podman run --rm -it \
  -v ./data:/app/data:Z \
  smart-parking-lot \
  uv run python manage.py migrate
```

Run tests in the container:

```bash
podman run --rm -it smart-parking-lot uv run python manage.py test
```

Start the development server with an explicit database path if needed:

```bash
podman run --rm -it \
  -p 8000:8000 \
  -e DJANGO_SQLITE_PATH=/app/data/db.sqlite3 \
  -v ./data:/app/data:Z \
  smart-parking-lot \
  uv run python manage.py runserver 0.0.0.0:8000
```
