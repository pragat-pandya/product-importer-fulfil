# Quick Test Guide

## Test CSV Import Feature

### 1. Create a Test CSV File

```bash
cat > products.csv << 'EOF'
sku,name,description,active
WIDGET-001,Premium Widget,High-quality widget for professionals,true
WIDGET-002,Basic Widget,Entry-level widget,true
WIDGET-003,Pro Widget,Professional-grade widget,false
EOF
```

### 2. Upload the CSV

```bash
# Upload and capture task ID
TASK_ID=$(curl -X POST -F "file=@products.csv" \
  http://localhost:8000/api/v1/products/upload -s \
  | python3 -c "import sys, json; print(json.load(sys)['task_id'])")

echo "Task ID: $TASK_ID"
```

### 3. Check Status

```bash
# Check status (simplified endpoint with clean state names)
curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status | python3 -m json.tool
```

Or watch in real-time:

```bash
# Watch status updates
watch -n 1 "curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status | python3 -m json.tool"
```

Alternative - detailed progress:

```bash
# Detailed progress with all fields
curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/progress | python3 -m json.tool
```

### 4. Get Final Results

```bash
curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/result | python3 -m json.tool
```

### 5. Verify Database

```bash
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "SELECT sku, name, active FROM products WHERE sku LIKE 'WIDGET-%' ORDER BY sku;"
```

## Test Case-Insensitive Update

### 1. Create Update CSV (with lowercase SKU)

```bash
cat > products_update.csv << 'EOF'
sku,name,description,active
widget-001,UPDATED Premium Widget,This was updated with lowercase SKU,true
WIDGET-004,New Widget,Brand new product,true
EOF
```

### 2. Upload Update

```bash
curl -X POST -F "file=@products_update.csv" \
  http://localhost:8000/api/v1/products/upload -s | python3 -m json.tool
```

### 3. Verify Case-Insensitive Update Worked

```bash
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "SELECT sku, name, description FROM products WHERE sku IN ('WIDGET-001', 'widget-001', 'WIDGET-004');"
```

Expected: `WIDGET-001` should be updated (not created as duplicate)

## Test Error Handling

### 1. Create Invalid CSV

```bash
cat > products_invalid.csv << 'EOF'
sku,name,description,active
,Missing SKU,This should fail,true
VALID-001,,Missing name should fail,true
VALID-002,This is valid,This should succeed,true
EOF
```

### 2. Upload and Check Errors

```bash
TASK_ID=$(curl -X POST -F "file=@products_invalid.csv" \
  http://localhost:8000/api/v1/products/upload -s \
  | python3 -c "import sys, json; print(json.load(sys)['task_id'])")

sleep 3

curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/result | python3 -m json.tool
```

Expected: 
- 1 product created (VALID-002)
- 2 errors (missing SKU and missing name)
- Error details provided

## Check All API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api/docs

# List all endpoints
curl -s http://localhost:8000/openapi.json | \
  python3 -c "import sys, json; data = json.load(sys); [print(path) for path in sorted(data['paths'].keys())]"
```

## Monitor Services

### Check Container Status

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Worker Logs

```bash
docker logs fulfil_worker -f
```

### View Backend Logs

```bash
docker logs fulfil_backend -f
```

### Check Database

```bash
# Connect to database
docker exec -it fulfil_postgres psql -U fulfil_user -d fulfil_db

# Count products
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "SELECT COUNT(*) as total_products FROM products;"

# View all products
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "SELECT sku, name, active, created_at FROM products ORDER BY created_at DESC LIMIT 10;"
```

### Check Redis

```bash
# Connect to Redis
docker exec -it fulfil_redis redis-cli

# Check progress keys
docker exec fulfil_redis redis-cli KEYS "celery-task-progress:*"
```

## Clean Up Test Data

```bash
# Delete test files
rm -f products.csv products_update.csv products_invalid.csv

# Delete test products from database
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "DELETE FROM products WHERE sku LIKE 'WIDGET-%' OR sku LIKE 'VALID-%';"
```

## Performance Test

### Generate Large CSV

```bash
python3 << 'EOF'
import csv

with open('large_products.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sku', 'name', 'description', 'active'])
    
    for i in range(10000):
        writer.writerow([
            f'PERF-{i:06d}',
            f'Performance Test Product {i}',
            f'This is test product number {i} for performance testing',
            'true' if i % 2 == 0 else 'false'
        ])

print("Generated 10,000 row CSV: large_products.csv")
EOF
```

### Upload and Monitor

```bash
# Upload
echo "Starting upload..."
TASK_ID=$(curl -X POST -F "file=@large_products.csv" \
  http://localhost:8000/api/v1/products/upload -s \
  | python3 -c "import sys, json; print(json.load(sys)['task_id'])")

echo "Task ID: $TASK_ID"
echo "Monitoring progress..."

# Monitor
while true; do
  PROGRESS=$(curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/progress)
  STATUS=$(echo $PROGRESS | python3 -c "import sys, json; print(json.load(sys)['status'])")
  PERCENT=$(echo $PROGRESS | python3 -c "import sys, json; print(json.load(sys).get('percent', 0))")
  
  echo "Status: $STATUS - Progress: $PERCENT%"
  
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILURE" ]; then
    break
  fi
  
  sleep 2
done

echo ""
echo "Final result:"
curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/result | python3 -m json.tool
```

## Troubleshooting Commands

### Restart All Services

```bash
cd /Users/pragat/Documents/fulFil
docker-compose restart
```

### Rebuild Containers

```bash
cd /Users/pragat/Documents/fulFil
docker-compose down
docker-compose up --build -d
```

### Check Disk Usage

```bash
docker system df
```

### View Upload Directory

```bash
docker exec fulfil_backend ls -lh /app/uploads/
```

### Clear Upload Directory

```bash
docker exec fulfil_backend rm -rf /app/uploads/*
```

