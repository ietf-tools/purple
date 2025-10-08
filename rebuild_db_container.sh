#!/bin/bash
set -e -o pipefail

echo "Stopping db container..."
docker compose stop db

echo "Removing db container and volume..."
docker compose rm -fv db
docker volume rm -f purple_postgresdb-data

echo "Creating db container..."
docker compose create db

echo "Starting db container..."
docker compose start db

echo "Done!"
