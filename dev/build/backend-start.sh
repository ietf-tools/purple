#!/bin/bash -e

# Bare call to trap seems to help TERM signals exit during sleep
trap

if ! ./manage.py migrate --check ; then
    echo "Unapplied migrations found, waiting to start..."
    sleep 5
    while ! ./manage.py migrate --check ; do
        echo "... still waiting for migrations..."
        sleep 5
    done
fi

echo "Starting Purple API server..."

# trap TERM and shut down gunicorn
cleanup () {
    if [[ -n "${gunicorn_pid}" ]]; then
        echo "Terminating gunicorn..."
        kill -TERM "${gunicorn_pid}"
        wait "${gunicorn_pid}"
    fi
}

trap 'trap "" TERM; cleanup' TERM

# start gunicorn in the background so we can trap the TERM signal
gunicorn \
    -c /workspace/gunicorn.conf.py \
    --workers "${PURPLE_GUNICORN_WORKERS:-9}" \
    --max-requests "${PURPLE_GUNICORN_MAX_REQUESTS:-0}" \
    --timeout "${PURPLE_GUNICORN_TIMEOUT:-180}" \
    --bind :8000 \
    --log-level "${PURPLE_GUNICORN_LOG_LEVEL:-info}" \
    --capture-output \
    --access-logfile -\
    ${PURPLE_GUNICORN_EXTRA_ARGS} \
    purple.wsgi:application &
gunicorn_pid=$!
wait "${gunicorn_pid}"
