#!/bin/bash
#
# Environment config:
#
#  CONTAINER_ROLE - backend, beat, celery, or migrations
#
case "${CONTAINER_ROLE:-backend}" in
    backend)
        exec ./backend-start.sh
        ;;
    beat)
        exec ./celery-start.sh beat --loglevel=INFO
        ;;
    celery)
        exec ./celery-start.sh worker --loglevel=INFO
        ;;
    migrations)
        exec ./migration-start.sh
        ;;
    *)
        echo "Unknown role '${CONTAINER_ROLE}'"
        exit 255
esac
