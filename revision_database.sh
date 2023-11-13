#!/bin/bash
# Creates the Users tables and inserts some intial data. 

# Start the app in one terminal, Open another and launch this script after making any 
# revisions with Alembic. Edit as needed.

set -e

cd "$(dirname "$0")"

if docker-compose ps | grep -q Up; then
    echo "Running Alembic migrations..."
    sleep 3
    docker-compose exec web alembic upgrade head
    echo "Migrations complete. "
    docker-compose exec web python /app/app/startup_scripts/initial_data.py
else
    echo "Docker Compose services are not running."
fi