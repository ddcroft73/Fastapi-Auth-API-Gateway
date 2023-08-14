#!/bin/bash
# wakes up the DB, creates the Users tables and inserts some intial data. THis
# script only needs to be ran once. 
# After using this script,the stack can be started with 'docker-compose up'

# THis little script I have found is good anytine i revise the DB. 
set -e

cd "$(dirname "$0")"

if docker-compose ps | grep -q Up; then
    echo "Attempting to wake the Database..."
    sleep 3
    echo "Running Alembic migrations..."
    sleep 3
    docker-compose exec web alembic upgrade head
    echo "Migrations complete."
    sleep 3
    #docker-compose exec web python /app/app/startup_scripts/initial_data.py
else
    echo "Docker Compose services are not running."
fi