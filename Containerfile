FROM ghcr.io/astral-sh/uv:0.8.22 AS uv

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV DJANGO_SQLITE_PATH=/app/data/db.sqlite3

WORKDIR /app

COPY --from=uv /uv /uvx /usr/local/bin/
COPY src/pyproject.toml src/uv.lock ./

RUN uv sync --frozen --no-dev

COPY src/ ./
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
