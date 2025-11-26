# API Endpoints Reference

## Overview

The FulFil Product Importer provides multiple API endpoints for different use cases. Here's a quick reference guide.

## Product Import Endpoints Comparison

### Upload Endpoint

```
POST /api/v1/products/upload
```

**Purpose:** Upload a CSV file for processing

**When to use:** Start of every import workflow

**Response:**
```json
{
  "task_id": "uuid",
  "status": "submitted",
  "message": "File uploaded successfully. Processing started.",
  "filename": "products.csv"
}
```

---

### Status Endpoint (Recommended) ⭐

```
GET /api/v1/products/upload/{task_id}/status
```

**Purpose:** Get simplified status with clean state names

**When to use:** 
- Building user-facing applications
- Need simple state machine (Pending → Processing → Completed/Failed)
- Want consistent, predictable responses

**Response:**
```json
{
  "task_id": "uuid",
  "state": "Processing",              // ⭐ Clean state names
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
- `Pending` - Task queued, not started
- `Processing` - Currently running
- `Completed` - Finished successfully
- `Failed` - Encountered an error

**Error Handling:**
- ✅ Graceful fallback to Celery if Redis unavailable
- ✅ Returns `Pending` for non-existent tasks (no 404 errors)
- ✅ Includes error messages in response
- ✅ 503 only if Redis connection completely fails

---

### Progress Endpoint (Detailed)

```
GET /api/v1/products/import/{task_id}/progress
```

**Purpose:** Get detailed progress with raw Celery states

**When to use:**
- Need all available fields
- Debugging or advanced monitoring
- Want raw Celery state values

**Response:**
```json
{
  "task_id": "uuid",
  "status": "PROGRESS",              // Raw Celery state
  "current": 5000,
  "total": 10000,
  "created": 3000,
  "updated": 2000,
  "errors": 0,
  "percent": 50,
  "message": "Processing...",
  "error": null
}
```

**Status Values:**
- `PENDING` - Queued
- `PROGRESS` - Running
- `SUCCESS` - Completed
- `FAILURE` - Failed

---

### Result Endpoint

```
GET /api/v1/products/import/{task_id}/result
```

**Purpose:** Get final detailed results after completion

**When to use:**
- Task is completed
- Need full statistics and error details
- Building reports or summaries

**Response:**
```json
{
  "status": "success",
  "task_id": "uuid",
  "result": {
    "status": "completed",
    "message": "CSV import completed successfully",
    "total_rows": 10000,
    "processed_rows": 9998,
    "created": 5000,
    "updated": 4998,
    "errors": 2,
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

---

## Recommended Usage Patterns

### Pattern 1: Simple Frontend (Recommended)

Use the **status endpoint** for clean, predictable state handling:

```typescript
async function monitorImport(taskId: string) {
  while (true) {
    const { state, progress_percent, error } = await fetch(
      `/api/v1/products/upload/${taskId}/status`
    ).then(r => r.json());
    
    switch (state) {
      case 'Pending':
        showLoading('Queued...');
        break;
      case 'Processing':
        showProgress(progress_percent);
        break;
      case 'Completed':
        showSuccess();
        return;
      case 'Failed':
        showError(error);
        return;
    }
    
    await sleep(2000);
  }
}
```

### Pattern 2: Advanced Monitoring

Use **progress endpoint** for detailed monitoring:

```python
def monitor_detailed(task_id: str):
    while True:
        resp = requests.get(f'/api/v1/products/import/{task_id}/progress')
        data = resp.json()
        
        # Access all fields
        print(f"Status: {data['status']}")
        print(f"Progress: {data['current']}/{data['total']}")
        print(f"Created: {data['created']}, Updated: {data['updated']}")
        print(f"Errors: {data['errors']}")
        
        if data['status'] in ['SUCCESS', 'FAILURE']:
            break
        
        time.sleep(2)
```

### Pattern 3: Report Generation

Use **result endpoint** after completion:

```bash
# Wait for completion
while [ "$(curl -s /api/v1/products/upload/$TASK_ID/status | jq -r '.state')" != "Completed" ]; do
  sleep 2
done

# Get detailed results
curl -s /api/v1/products/import/$TASK_ID/result | jq > import_report.json
```

---

## Quick Decision Guide

**Choose `/upload/{id}/status` if you:**
- ✅ Building a user-facing application
- ✅ Want simple state names (Pending, Processing, Completed, Failed)
- ✅ Need reliable error handling
- ✅ Want consistent response structure

**Choose `/import/{id}/progress` if you:**
- 🔍 Need raw Celery states
- 🔍 Want all available fields
- 🔍 Building monitoring/debugging tools
- 🔍 Need backward compatibility

**Choose `/import/{id}/result` if you:**
- 📊 Task is already completed
- 📊 Need full error details
- 📊 Building reports or analytics
- 📊 Want comprehensive statistics

---

## Celery Task Management Endpoints

### View Active Workers

```
GET /api/v1/celery/workers
```

Get information about active Celery workers, registered tasks, and statistics.

### Submit Test Task

```
POST /api/v1/celery/test
```

Submit a test task to verify Celery is working.

### Check Task Status

```
GET /api/v1/celery/task/{task_id}
```

Get status of any Celery task (not just imports).

### Cancel Task

```
DELETE /api/v1/celery/task/{task_id}
```

Revoke/cancel a running task.

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid file type. Only CSV files are allowed."
}
```

### 404 Not Found
```json
{
  "detail": "Task not found or expired."
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred: {error_message}"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Redis connection failed. Progress tracking unavailable."
}
```

---

## Complete API Map

```
Health & Status
├── GET  /                          Root status
├── GET  /health                    Health check
└── GET  /api/v1/hello             Demo endpoint

Product Import
├── POST /api/v1/products/upload                      Upload CSV
├── GET  /api/v1/products/upload/{id}/status         Check status ⭐
├── GET  /api/v1/products/import/{id}/progress       Detailed progress
└── GET  /api/v1/products/import/{id}/result         Final results

Celery Management
├── GET    /api/v1/celery/workers                    View workers
├── POST   /api/v1/celery/test                       Test task
├── GET    /api/v1/celery/task/{id}                  Task status
└── DELETE /api/v1/celery/task/{id}                  Cancel task

Documentation
└── GET  /api/docs                  OpenAPI/Swagger docs
```

---

## Example Workflow

```bash
# 1. Upload CSV
TASK_ID=$(curl -X POST -F "file=@products.csv" \
  http://localhost:8000/api/v1/products/upload \
  | jq -r '.task_id')

# 2. Monitor with status endpoint (recommended)
while true; do
  STATE=$(curl -s http://localhost:8000/api/v1/products/upload/$TASK_ID/status \
    | jq -r '.state')
  
  case "$STATE" in
    "Completed")
      echo "✅ Import complete!"
      break
      ;;
    "Failed")
      echo "❌ Import failed!"
      break
      ;;
    *)
      echo "⏳ State: $STATE"
      ;;
  esac
  
  sleep 2
done

# 3. Get detailed results
curl -s http://localhost:8000/api/v1/products/import/$TASK_ID/result | jq
```

---

## See Also

- [CSV Import Guide](./CSV_IMPORT_GUIDE.md) - Detailed CSV import documentation
- [Quick Test Guide](./QUICK_TEST.md) - Quick testing commands
- [Celery Setup](./CELERY_SETUP.md) - Celery configuration details
- [API Docs](http://localhost:8000/api/docs) - Interactive OpenAPI documentation

