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
EXPOSE 8044
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8044"]
