#!/bin/sh
set -e

# Run alembic migrations ONLY if DATABASE_URL is a real external DB (not localhost)
if [ -n "$DATABASE_URL" ] && echo "$DATABASE_URL" | grep -qv "localhost"; then
    echo "==> Running Alembic migrations..."
    alembic upgrade head
    echo "==> Migrations done."
else
    echo "==> Skipping Alembic (no external DATABASE_URL). Tables will be created by init_db()."
fi

echo "==> Starting SpiderGlass AI backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
