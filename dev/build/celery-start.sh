#!/bin/bash -e
#
# Startup script for the celery container
#

# specify binary locations
CELERY=/usr/local/bin/celery
MANAGE_PY=./manage.py

migrations_applied_for () {
    local DATABASE=${1:-default}
    $MANAGE_PY migrate --check --database "$DATABASE"
}

migrations_all_applied () {
    migrations_applied_for default
}

if ! migrations_all_applied; then
    echo "Unapplied migrations found, waiting to start..."
    sleep 5
    while ! migrations_all_applied ; do
        echo "... still waiting for migrations..."
        sleep 5
    done
fi

echo "Starting Purple celery container..."

# trap TERM and shut down celery
cleanup () {
  # Cleanly terminate the celery app by sending it a TERM, then waiting for it to exit.
  if [[ -n "${celery_pid}" ]]; then
    echo "Gracefully terminating celery worker..."
    kill -TERM "${celery_pid}"
    wait "${celery_pid}"
  fi
}

trap 'trap "" TERM; cleanup' TERM

# start celery in the background so we can trap the TERM signal
$CELERY --app="${CELERY_APP:-purple}" worker &
celery_pid=$!

# Just chill while celery does its thang
wait "${celery_pid}"
