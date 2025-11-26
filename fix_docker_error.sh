#!/bin/bash
# Fix Docker ContainerConfig Error

echo "=== Stopping all containers ==="
docker-compose down

echo -e "\n=== Removing old containers ==="
docker-compose rm -f backend

echo -e "\n=== Removing backend image ==="
docker rmi fulfil_backend:latest 2>/dev/null || echo "Image already removed"

echo -e "\n=== Rebuilding backend ==="
docker-compose build --no-cache backend

echo -e "\n=== Starting all services ==="
docker-compose up -d

echo -e "\n=== Waiting 10 seconds for startup ==="
sleep 10

echo -e "\n=== Checking status ==="
docker-compose ps

echo -e "\n=== Testing backend ==="
curl -s http://localhost:8009/api/v1/hello || echo "Backend not responding yet"

