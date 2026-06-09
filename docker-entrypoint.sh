#!/bin/sh
set -e

if [ "${RUN_DB_MIGRATIONS:-true}" = "true" ]; then
  attempt=0
  max=10
  until alembic upgrade head; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge "$max" ]; then
      echo "Alembic failed after ${max} attempts"
      exit 1
    fi
    echo "Database not ready, retry ${attempt}/${max}..."
    sleep 3
  done
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
