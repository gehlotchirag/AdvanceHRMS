#!/bin/bash
set -e

echo "Starting Horilla HR..."

wait_for_postgres() {
  if [ -n "${SKIP_DB_WAIT:-}" ]; then
    echo "SKIP_DB_WAIT is set; not waiting for PostgreSQL."
    return 0
  fi

  # On Railway, TCP probes with `nc` often do not match how Postgres is exposed (internal DNS,
  # proxy, IPv6). Waiting here can loop forever while health checks fail. Django connects when needed.
  if [ -n "${RAILWAY_ENVIRONMENT:-}" ] && [ -z "${FORCE_DB_WAIT:-}" ]; then
    echo "RAILWAY_ENVIRONMENT is set; skipping TCP wait for Postgres (set FORCE_DB_WAIT=1 to enable)."
    return 0
  fi

  _wait_tcp() {
    _host="$1"
    _port="$2"
    _max="${DB_WAIT_MAX_SECONDS:-120}"
    _n=0
    _limit=$((_max * 2))
    echo "Waiting (max ${_max}s) for TCP ${_host}:${_port}..."
    while ! nc -z "$_host" "$_port"; do
      _n=$((_n + 1))
      if [ "$_n" -ge "$_limit" ]; then
        echo "ERROR: Postgres TCP not reachable at ${_host}:${_port} after ${_max}s. Fix DATABASE_URL / network or set SKIP_DB_WAIT=1."
        exit 1
      fi
      sleep 0.5
    done
    echo "PostgreSQL TCP is reachable."
  }

  if [ -n "${DATABASE_URL:-}" ]; then
    DB_HOST=$(python3 -c "from urllib.parse import urlparse; import os; u=urlparse(os.environ.get('DATABASE_URL','')); print(u.hostname or '')")
    DB_PORT=$(python3 -c "from urllib.parse import urlparse; import os; u=urlparse(os.environ.get('DATABASE_URL','')); print(u.port or 5432)")
    if [ -n "$DB_HOST" ]; then
      _wait_tcp "$DB_HOST" "$DB_PORT"
      return 0
    fi
    echo "Could not parse DATABASE_URL host; falling back to PGHOST/PGPORT."
  fi

  _wait_tcp "${PGHOST:-db}" "${PGPORT:-5432}"
}

wait_for_postgres

# Migrations are slow; collectstatic is usually faster. Set SKIP_STARTUP_MIGRATE=1 and
# run migrate via Railway **Settings → Deploy → Pre-deploy command** (see RAILWAY.md).
# Pre-deploy does not persist filesystem changes, so collectstatic always runs here.
if [ -z "${SKIP_STARTUP_MIGRATE:-}" ]; then
  python manage.py migrate --noinput
fi
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
