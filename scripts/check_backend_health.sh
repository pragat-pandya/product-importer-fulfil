#!/bin/bash
# Backend Health Check Script

echo "=== Docker Services Status ==="
docker-compose ps

echo ""
echo "=== Backend Container Logs (last 50 lines) ==="
docker-compose logs --tail=50 backend

echo ""
echo "=== Checking if backend container is running ==="
if docker ps | grep -q fulfil_backend; then
    echo "✓ Backend container is running"
else
    echo "✗ Backend container is NOT running"
    echo ""
    echo "=== Attempting to start backend ==="
    docker-compose up -d backend
    sleep 5
    docker-compose logs --tail=20 backend
fi

echo ""
echo "=== Testing backend health endpoint ==="
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
curl -v "${BACKEND_URL}/health" || echo "Failed to connect to backend"

echo ""
echo "=== Testing backend root endpoint ==="
curl -v "${BACKEND_URL}/" || echo "Failed to connect to backend"

echo ""
echo "=== Checking for Python import errors ==="
docker-compose exec -T backend python -c "from app.services.import_service import ImportService; print('✓ ImportService imported successfully')" 2>&1 || echo "✗ Import error detected"

echo ""
echo "=== Checking pandas version and errors module ==="
docker-compose exec -T backend python -c "import pandas as pd; print(f'Pandas version: {pd.__version__}'); import pandas.errors; print('✓ pandas.errors available')" 2>&1 || echo "✗ pandas.errors not available"

