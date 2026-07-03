FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app
RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
RUN poetry install --no-interaction --no-ansi
COPY --from=frontend-build /frontend/dist /app/frontend/dist
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY main.py .
COPY _alembic_helpers.py .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
# Host and port are configured via APP_HOST/APP_PORT env vars in entrypoint.sh
