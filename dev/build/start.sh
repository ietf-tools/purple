#!/bin/bash
#
# Environment config:
#
#  CONTAINER_ROLE - backend, celery, or migrations
#
case "${CONTAINER_ROLE:-backend}" in
    backend)
        exec ./backend-start.sh
        ;;
    celery)
        exec ./celery-start.sh
        ;;
    migrations)
        exec ./migration-start.sh
        ;;
    *)
        echo "Unknown role '${CONTAINER_ROLE}'"
        exit 255
esac
