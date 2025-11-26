# Celery Configuration Guide

## Overview

Celery is fully configured and integrated with the FulFil Product Importer application. The worker is running in Docker and connected to Redis as both broker and result backend.

## Architecture

```
backend/app/
├── core/
│   └── celery_app.py          # Celery application configuration
├── tasks/
│   └── product_tasks.py       # Product-related async tasks
└── api/
    └── celery_routes.py       # API endpoints for task management
```

## Configuration Details

### Celery App (`app/core/celery_app.py`)

**Broker & Backend:** Redis (`redis://redis:6379/0`)

**Key Settings:**
- **Serialization:** JSON only (secure)
- **Time Limits:** 1 hour hard limit, 55 minutes soft limit
- **Task Acknowledgment:** Late acknowledgment (after completion)
- **Worker:** Prefetch 1 task at a time (optimal for long-running tasks)
- **Results:** Expire after 1 hour, persistent storage

**Signal Handlers:**
- `worker_ready`: Logs when worker starts
- `worker_shutdown`: Logs when worker stops

## Registered Tasks

### 1. Test Task
```python
app.tasks.product_tasks.test_task
```
Verifies Celery is working correctly. Returns success message.

### 2. CSV Import Task (Placeholder)
```python
app.tasks.product_tasks.process_csv_import
```
Will process large CSV imports (500k+ rows) asynchronously.

**Parameters:**
- `file_path`: Path to CSV file
- `user_id`: Optional user who initiated import
- `options`: Optional processing options

**Features:**
- Progress tracking
- Retry on failure (3 attempts, 5-minute delay)
- Time limits enforced
- Database session management via base task class

### 3. Cleanup Task
```python
app.tasks.product_tasks.cleanup_old_imports
```
Periodic cleanup of old import files and records.

## API Endpoints

All endpoints are prefixed with `/api/v1/celery`

### GET `/workers`
Get information about active Celery workers.

**Response:**
```json
{
  "status": "success",
  "workers": {
    "active": {...},
    "stats": {...},
    "registered_tasks": [...]
  }
}
```

### POST `/test`
Submit a test task to verify Celery is working.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "submitted",
  "message": "Test task has been submitted to the worker"
}
```

### GET `/task/{task_id}`
Check the status of a submitted task.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "SUCCESS|PENDING|FAILURE",
  "result": {...},
  "error": null
}
```

### DELETE `/task/{task_id}`
Revoke (cancel) a running task.

## Docker Configuration

### Worker Service
```yaml
worker:
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=2
  environment:
    DATABASE_URL: postgresql+asyncpg://...
    REDIS_URL: redis://redis:6379/0
```

**Worker Pool:** Solo (for macOS/development compatibility)
**Concurrency:** 2 workers

## Usage Examples

### Via Python
```python
from app.tasks.product_tasks import test_task

# Submit task
result = test_task.apply_async()

# Get task ID
task_id = result.id

# Wait for result (blocking)
task_result = result.get(timeout=10)
```

### Via API
```bash
# Submit a test task
curl -X POST http://localhost:8000/api/v1/celery/test

# Check task status
curl http://localhost:8000/api/v1/celery/task/{task_id}

# View active workers
curl http://localhost:8000/api/v1/celery/workers
```

### Via CLI
```bash
# Check worker status
docker exec fulfil_backend celery -A app.core.celery_app inspect active

# See registered tasks
docker exec fulfil_backend celery -A app.core.celery_app inspect registered

# Purge all tasks
docker exec fulfil_backend celery -A app.core.celery_app purge
```

## Monitoring

### View Worker Logs
```bash
docker logs fulfil_worker -f
```

### Worker Status
```bash
docker ps | grep fulfil_worker
```

### Redis Connection Test
```bash
docker exec fulfil_redis redis-cli ping
# Should return: PONG
```

## Testing

The Celery setup has been verified:
✅ Worker connects to Redis successfully
✅ Tasks are discovered and registered automatically
✅ Tasks can be submitted and executed
✅ Task results are stored and retrievable
✅ API endpoints work correctly

**Test Results:**
```
Task: app.tasks.product_tasks.test_task
Status: SUCCESS
Execution Time: ~0.001s
Message: Celery worker is functioning correctly! 🎉
```

## Future Enhancements

1. **Task Queues**: Separate queues for CSV import vs. other tasks
2. **Task Priorities**: Priority queue for urgent imports
3. **Beat Scheduler**: Periodic tasks (cleanup, reports)
4. **Monitoring**: Flower UI for task monitoring
5. **Rate Limiting**: Prevent worker overload

## Troubleshooting

### Worker Not Starting
```bash
docker logs fulfil_worker
# Check for import errors or configuration issues
```

### Tasks Not Executing
```bash
# Check Redis connection
docker exec fulfil_redis redis-cli ping

# Check worker is listening
docker exec fulfil_backend celery -A app.core.celery_app inspect active
```

### Task Stuck in PENDING
- Worker might be down - check `docker ps`
- Redis connection issue - verify network
- Task routing misconfiguration - check task routes

## References

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

