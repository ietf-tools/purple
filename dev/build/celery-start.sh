#!/bin/bash -e
#
# Startup script for the celery container
#

# specify celery location
CELERY=/home/dev/.local/bin/celery

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
