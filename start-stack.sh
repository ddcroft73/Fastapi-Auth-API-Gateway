#!/bin/bash

# Get host IP
HOST_IP=$(python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); s.close()")
export HOST_IP_ADDRESS=$HOST_IP

docker-compose up --build
