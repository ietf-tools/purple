#!/bin/bash
#
# Startup script for the celery container
#

cd /workspace

# Install requirements.txt dependencies
echo "Installing dependencies from requirements.txt..."
pip3 --disable-pip-version-check --no-cache-dir install --user --no-warn-script-location -r requirements.txt

# specify celery location
CELERY=/home/dev/.local/bin/celery

# Wait for DB container
echo "Waiting for DB container to come online..."
/usr/local/bin/wait-for db:5432 -- echo "PostgreSQL ready"

# Prepare to run celery
cleanup () {
  # Cleanly terminate the celery app by sending it a TERM, then waiting for it to exit.
  if [[ -n "${celery_pid}" ]]; then
    echo "Gracefully terminating celery worker."
    kill -TERM "${celery_pid}"
    wait "${celery_pid}"
  fi
}
trap 'trap "" TERM; cleanup' TERM
echo "Starting celery..."
watchmedo auto-restart \
          --patterns '*.py' \
          --directory . \
          --recursive \
          --debounce-interval 5 \
          -- \
          $CELERY --app="${CELERY_APP:-purple}" worker &
celery_pid=$!

# Just chill while celery does its thang
wait "${celery_pid}"
