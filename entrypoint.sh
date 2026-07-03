#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete. Starting application..."

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8044}"

exec uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT"
