#!/bin/bash
# Backend Crash Diagnostic Script

echo "=== Backend Container Logs ==="
docker-compose logs backend --tail=100

echo -e "\n=== Check if Uvicorn is running inside container ==="
docker-compose exec backend ps aux | grep uvicorn

echo -e "\n=== Check Python process ==="
docker-compose exec backend ps aux | grep python

echo -e "\n=== Test from inside container ==="
docker-compose exec backend curl -s http://localhost:8009/api/v1/hello || echo "FAILED from inside container"

echo -e "\n=== Check port 8000 inside container ==="
docker-compose exec backend netstat -tlnp 2>/dev/null | grep 8000 || echo "Port 8000 not listening"

