#!/bin/bash
# wakes up the DB, creates the Users tables and inserts some intial data. THis
# script only needs to be ran once. After that the stack can be started with 'docker-compose up'

set -e

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Get the basename of the current directory
COMPOSE_PROJECT_NAME=$(basename "$PWD")

# Check if any services defined in docker-compose.yml are currently running
if docker-compose ps | grep -q Up; then
  echo "Attempting to wake the Database...."
  sleep 3
 # docker-compose exec web python /app/app/scripts/backend_prestart.py
  sleep 5
  echo "Running Alembic migrations..."
  sleep 3
  #docker-compose exec web alembic upgrade head 
  echo "Creating first super user..."
  sleep 3
 # docker-compose exec web python /app/app/scripts/initial_data.py
else
  echo "Docker Compose services are not running."
fi