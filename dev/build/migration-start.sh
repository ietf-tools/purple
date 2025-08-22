#!/bin/bash -e

echo "Running migrations..."
./manage.py migrate

echo "Populating initial history..."
./manage.py populate_history --auto

echo "Done!"
