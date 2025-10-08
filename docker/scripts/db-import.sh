#!/bin/bash
set -e -o pipefail
DUMPFILE=/db-dumps/purple.dump

echo "Drop DB if it exists..."
dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"

echo "Create empty DB..."
createdb -U "$POSTGRES_USER" -T template0 "$POSTGRES_DB"

if [ -f "$DUMPFILE" ]; then
    echo "Import DB dump into $POSTGRES_DB..."
    pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$DUMPFILE"
else
    echo "No file to import, skipping..."
fi

echo "Done!"
