#!/bin/sh
set -eu

max_retries="${DB_CONNECTION_MAX_RETRIES:-30}"
retry_interval="${DB_CONNECTION_RETRY_INTERVAL:-2}"
attempt=1

until python manage.py shell -c "from django.db import connection; connection.ensure_connection()" >/dev/null 2>&1; do
    if [ "$attempt" -ge "$max_retries" ]; then
        echo "Database did not become available after ${max_retries} attempts." >&2
        exit 1
    fi

    echo "Waiting for MySQL (${attempt}/${max_retries})..."
    attempt=$((attempt + 1))
    sleep "$retry_interval"
done

echo "MySQL is ready. Starting Django."
exec "$@"
