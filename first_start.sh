#!/bin/bash
# wakes up the DB, creates the Users tables and inserts some intial data. THis
# script only needs to be ran once. 
# After using this script,the stack can be started with 'docker-compose up'

set -e

cd "$(dirname "$0")"

if docker-compose ps | grep -q Up; then
    echo "Attempting to wake the Database..."
    sleep 3
   # docker-compose exec web python /app/app/startup_scripts/backend_prestart.py
    sleep 5
    echo "Running Alembic migrations..."
    sleep 3
    docker-compose exec web alembic upgrade head 
    echo "Creating first super user..."
    sleep 3
    docker-compose exec web python /app/app/startup_scripts/initial_data.py
else
    echo "Docker Compose services are not running."
fi