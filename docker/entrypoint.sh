#!/bin/bash
set -e

echo "Starting Horilla HR..."

wait_for_postgres() {
  if [ -n "${SKIP_DB_WAIT:-}" ]; then
    echo "SKIP_DB_WAIT is set; not waiting for PostgreSQL."
    return 0
  fi

  if [ -n "${DATABASE_URL:-}" ]; then
    echo "Waiting for PostgreSQL (from DATABASE_URL)..."
    DB_HOST=$(python3 -c "from urllib.parse import urlparse; import os; u=urlparse(os.environ.get('DATABASE_URL','')); print(u.hostname or '')")
    DB_PORT=$(python3 -c "from urllib.parse import urlparse; import os; u=urlparse(os.environ.get('DATABASE_URL','')); print(u.port or 5432)")
    if [ -n "$DB_HOST" ]; then
      while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 0.5
      done
      echo "PostgreSQL is ready!"
      return 0
    fi
    echo "Could not parse DATABASE_URL host; falling back to PGHOST/PGPORT."
  fi

  echo "Waiting for PostgreSQL at ${PGHOST:-db}:${PGPORT:-5432}..."
  while ! nc -z "${PGHOST:-db}" "${PGPORT:-5432}"; do
    sleep 0.1
  done
  echo "PostgreSQL is ready!"
}

wait_for_postgres

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
