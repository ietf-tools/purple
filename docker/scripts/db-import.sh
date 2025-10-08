#!/bin/bash
set -e

echo "Drop DB if it exists..."
dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"

echo "Import DB dump into $POSTGRES_DB..."
createdb -U "$POSTGRES_USER" -T template0 "$POSTGRES_DB"
pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB" purple.dump

echo "Done!"
