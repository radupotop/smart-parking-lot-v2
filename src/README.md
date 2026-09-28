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
