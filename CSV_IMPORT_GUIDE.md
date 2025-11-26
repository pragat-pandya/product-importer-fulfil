# CSV Import Feature Guide

## Overview

The FulFil Product Importer includes a robust CSV import system capable of processing large files (500k+ rows) asynchronously with progress tracking, validation, and case-insensitive duplicate handling.

## Features

✅ **Chunked Processing** - Memory-efficient processing of large CSV files  
✅ **Async Background Tasks** - Non-blocking imports using Celery  
✅ **Progress Tracking** - Real-time progress updates via Redis  
✅ **Case-Insensitive Upsert** - Smart duplicate handling based on SKU  
✅ **Validation** - Row-level validation with detailed error reporting  
✅ **Auto-cleanup** - Temporary files are automatically removed after processing  

## Architecture

```
┌──────────────┐
│ Upload CSV   │
│  (FastAPI)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌──────────────┐
│ Save to Temp │─────▶│ Trigger Task │
│  Directory   │      │   (Celery)   │
└──────────────┘      └──────┬───────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Process CSV  │
                      │  in Chunks   │
                      │  (Pandas)    │
                      └──────┬───────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
         ┌──────────────┐         ┌──────────────┐
         │  Validate    │         │   Update     │
         │    Rows      │         │  Progress    │
         │              │         │  (Redis)     │
         └──────┬───────┘         └──────────────┘
                │
                ▼
         ┌──────────────┐
         │    Upsert    │
         │  (ON CONFLICT│
         │   DO UPDATE) │
         └──────────────┘
```

## CSV Format

### Required Columns
- `sku` - Stock Keeping Unit (max 100 chars)
- `name` - Product name (max 255 chars)

### Optional Columns
- `description` - Product description (text)
- `active` - Boolean (true/false/yes/no/1/0)

### Example CSV

```csv
sku,name,description,active
PROD-001,Widget Pro,Premium widget with advanced features,true
PROD-002,Widget Lite,Basic widget for everyday use,true
PROD-003,Widget Max,Maximum performance widget,false
```

## API Endpoints

### 1. Upload CSV File

**POST** `/api/v1/products/upload`

Upload a CSV file for product import.

**Request:**
```bash
curl -X POST \
  -F "file=@products.csv" \
  http://localhost:8000/api/v1/products/upload
```

**Response:**
```json
{
  "task_id": "74af204a-7fa0-4abf-aa48-a96a001b50df",
  "status": "submitted",
  "message": "File uploaded successfully. Processing started.",
  "filename": "products.csv"
}
```

**Validation:**
- Only `.csv` files accepted
- Maximum file size: 100MB
- File must not be empty

### 2. Check Upload Status (Simplified)

**GET** `/api/v1/products/upload/{task_id}/status`

Get simplified status of an upload task with clean state names.

**Request:**
```bash
curl http://localhost:8000/api/v1/products/upload/{task_id}/status
```

**Response:**
```json
{
  "task_id": "178ad7fe-ac7f-4702-bb0a-1ba3c92124ce",
  "state": "Processing",
  "progress_percent": 50,
  "current": 5000,
  "total": 10000,
  "created": 3000,
  "updated": 2000,
  "errors": 0,
  "message": "Processing CSV file...",
  "error": null
}
```

**State Values:**
- `Pending` - Task is queued and waiting to start
- `Processing` - Currently processing the CSV file
- `Completed` - Import finished successfully
- `Failed` - Task encountered an error

**Error Handling:**
- Returns graceful response for non-existent task IDs
- Falls back to Celery if Redis is unavailable
- Returns 503 if Redis connection fails entirely
- Returns 500 for unexpected errors

### 3. Check Import Progress (Detailed)

**GET** `/api/v1/products/import/{task_id}/progress`

Get detailed real-time progress of an import task.

**Request:**
```bash
curl http://localhost:8000/api/v1/products/import/{task_id}/progress
```

**Response:**
```json
{
  "task_id": "74af204a-7fa0-4abf-aa48-a96a001b50df",
  "status": "PROGRESS",
  "current": 5000,
  "total": 10000,
  "created": 3000,
  "updated": 2000,
  "errors": 0,
  "percent": 50,
  "message": null,
  "error": null
}
```

**Status Values:**
- `PENDING` - Task is queued
- `PROGRESS` - Currently processing
- `SUCCESS` - Completed successfully
- `FAILURE` - Task failed

### 4. Get Final Results

**GET** `/api/v1/products/import/{task_id}/result`

Get detailed results after import completes.

**Request:**
```bash
curl http://localhost:8000/api/v1/products/import/{task_id}/result
```

**Response:**
```json
{
  "status": "success",
  "task_id": "74af204a-7fa0-4abf-aa48-a96a001b50df",
  "result": {
    "status": "completed",
    "message": "CSV import completed successfully",
    "total_rows": 10000,
    "processed_rows": 9998,
    "created": 5000,
    "updated": 4998,
    "errors": 2,
    "skipped": 0,
    "error_details": [
      {
        "row": 150,
        "error": "Row 150: SKU is required",
        "data": {...}
      }
    ]
  }
}
```

## Upsert Logic

The import uses PostgreSQL's `ON CONFLICT DO UPDATE` with a **case-insensitive** index on the SKU field.

### How It Works

1. **Check existing SKUs** (case-insensitive)
```sql
SELECT sku FROM products 
WHERE lower(sku) IN (lower('PROD-001'), lower('prod-001'))
```

2. **Insert with conflict handling**
```sql
INSERT INTO products (sku, name, description, active)
VALUES ('PROD-001', 'Product Name', 'Description', true)
ON CONFLICT (lower(sku)) 
DO UPDATE SET
  name = excluded.name,
  description = excluded.description,
  active = excluded.active,
  updated_at = now()
```

### Examples

| CSV SKU | DB SKU | Action |
|---------|--------|--------|
| `PROD-001` | `PROD-001` | **Update** existing |
| `prod-001` | `PROD-001` | **Update** existing (case-insensitive) |
| `PROD-002` | *(none)* | **Create** new |
| `PROD-003` | `prod-003` | **Update** existing |

## Validation Rules

### SKU Validation
- ✅ Required (not empty)
- ✅ Max 100 characters
- ✅ Trimmed of whitespace
- ✅ Case-insensitive uniqueness

### Name Validation
- ✅ Required (not empty)
- ✅ Max 255 characters
- ✅ Trimmed of whitespace

### Description Validation
- ✅ Optional
- ✅ Unlimited length
- ✅ `NULL` if empty

### Active Validation
- ✅ Optional (defaults to `true`)
- ✅ Accepts: `true`, `false`, `1`, `0`, `yes`, `no`, `active`
- ✅ Case-insensitive

## Performance

### Chunked Processing

Files are processed in chunks of **1,000 rows** to keep memory usage low:

```python
CHUNK_SIZE = 1000  # Rows per batch
```

For a 500,000 row CSV:
- **500 chunks** processed sequentially
- **~10-50MB** peak memory usage
- **5-15 minutes** total processing time

### Progress Updates

Progress is updated after each chunk and stored in Redis:

```
Key: celery-task-progress:{task_id}
Expiry: 1 hour
Data: JSON with current/total/stats
```

## Error Handling

### Row-Level Errors

Invalid rows are **skipped** with detailed error tracking:

```json
{
  "errors": 2,
  "error_details": [
    {
      "row": 150,
      "error": "Row 150: SKU is required",
      "data": {
        "sku": "",
        "name": "Product Name"
      }
    },
    {
      "row": 250,
      "error": "Row 250: Name is required",
      "data": {
        "sku": "PROD-250",
        "name": ""
      }
    }
  ]
}
```

### Task-Level Errors

If the task fails completely (file not found, database error):

```json
{
  "task_id": "...",
  "status": "FAILURE",
  "error": "File not found: /app/uploads/file.csv"
}
```

**Retry Logic:**
- Max retries: 3
- Retry delay: 5 minutes
- Exponential backoff

## Usage Examples

### Python Client

```python
import requests
import time

# Upload CSV
with open('products.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/products/upload',
        files={'file': f}
    )
task_id = response.json()['task_id']

# Poll for status (simplified endpoint)
while True:
    status = requests.get(
        f'http://localhost:8000/api/v1/products/upload/{task_id}/status'
    ).json()
    
    if status['state'] == 'Completed':
        print(f"✅ Import complete!")
        print(f"   Created: {status['created']}")
        print(f"   Updated: {status['updated']}")
        print(f"   Errors: {status['errors']}")
        break
    elif status['state'] == 'Failed':
        print(f"❌ Import failed: {status['error']}")
        break
    else:
        print(f"⏳ {status['state']}: {status['progress_percent']}%")
        time.sleep(2)
```

### JavaScript/TypeScript

```typescript
async function uploadCSV(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/v1/products/upload', {
    method: 'POST',
    body: formData,
  });
  
  const { task_id } = await response.json();
  return task_id;
}

async function pollStatus(taskId: string) {
  while (true) {
    const response = await fetch(
      `/api/v1/products/upload/${taskId}/status`
    );
    const status = await response.json();
    
    if (status.state === 'Completed') {
      console.log('Import complete!', status);
      return status;
    } else if (status.state === 'Failed') {
      throw new Error(status.error);
    }
    
    console.log(`${status.state}: ${status.progress_percent}%`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

### cURL

```bash
# Upload file
TASK_ID=$(curl -X POST -F "file=@products.csv" \
  http://localhost:8000/api/v1/products/upload \
  | jq -r '.task_id')

echo "Task ID: $TASK_ID"

# Check status (simplified endpoint)
while true; do
  STATE=$(curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status \
    | jq -r '.state')
  
  if [ "$STATE" = "Completed" ]; then
    echo "✅ Import complete!"
    curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status | jq
    break
  elif [ "$STATE" = "Failed" ]; then
    echo "❌ Import failed!"
    curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status | jq
    break
  fi
  
  echo "State: $STATE"
  sleep 2
done
```

## Testing

### Test CSV Creation

```bash
cat > test_products.csv << EOF
sku,name,description,active
TEST-001,Test Product 1,First test product,true
TEST-002,Test Product 2,Second test product,false
test-003,Test Product 3,Testing case-insensitive SKU,true
EOF
```

### Upload Test

```bash
curl -X POST -F "file=@test_products.csv" \
  http://localhost:8000/api/v1/products/upload
```

### Verify Database

```bash
docker exec fulfil_postgres psql -U fulfil_user -d fulfil_db \
  -c "SELECT * FROM products WHERE sku LIKE 'TEST-%' ORDER BY sku;"
```

## Troubleshooting

### Import Stuck in PENDING

**Cause:** Worker is not running or not processing tasks

**Solution:**
```bash
docker ps | grep fulfil_worker
docker logs fulfil_worker
docker-compose restart worker
```

### High Memory Usage

**Cause:** Processing very large files

**Solution:** Reduce chunk size in `app/services/import_service.py`:
```python
CHUNK_SIZE = 500  # Reduce from 1000
```

### Import Taking Too Long

**Cause:** Large file or slow database

**Optimization:**
1. Increase worker concurrency
2. Optimize database indexes
3. Use faster storage

### File Upload Fails

**Causes:**
- File too large (>100MB)
- Wrong file type (not CSV)
- Network timeout

**Solutions:**
- Split large files
- Increase upload timeout
- Check network connectivity

## Best Practices

✅ **Test with small files first** before importing large datasets  
✅ **Backup database** before large imports  
✅ **Monitor worker logs** during import  
✅ **Use meaningful SKUs** that won't conflict  
✅ **Validate CSV locally** before uploading  
✅ **Schedule large imports** during off-peak hours  

## References

- [Main Documentation](./README.md)
- [Celery Setup Guide](./CELERY_SETUP.md)
- [API Documentation](http://localhost:8000/api/docs)

