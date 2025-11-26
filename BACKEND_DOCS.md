# FulFil Backend Documentation

Complete technical documentation for the FulFil Product Importer backend system.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database & Models](#database--models)
3. [API Endpoints](#api-endpoints)
4. [CSV Import System](#csv-import-system)
5. [Webhook System](#webhook-system)
6. [Celery Background Tasks](#celery-background-tasks)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## Architecture Overview

### Tech Stack

- **Framework:** FastAPI 0.104+ (Python 3.11)
- **Database:** PostgreSQL 15 with asyncpg driver
- **ORM:** SQLAlchemy 2.0 (async)
- **Task Queue:** Celery with Redis broker
- **Migrations:** Alembic (async-compatible)
- **Validation:** Pydantic v2
- **HTTP Client:** httpx (async)

### Clean Architecture

```
app/
├── api/              # API Routes (Controllers)
├── services/         # Business Logic
├── repositories/     # Data Access Layer
├── models/           # SQLAlchemy Models
├── schemas/          # Pydantic Schemas
├── tasks/            # Celery Tasks
├── core/             # Core Configuration
└── db/               # Database Setup
```

### Design Principles

- **SOLID:** Single Responsibility, Dependency Injection
- **Async First:** All I/O operations are async
- **Type Safety:** Full Python type hints
- **Separation of Concerns:** Clear layer boundaries

---

## Database & Models

### Product Model

**Table:** `products`

```python
id: UUID (Primary Key)
sku: VARCHAR(100) - Unique, case-insensitive
name: VARCHAR(255) - Required
description: TEXT - Optional
active: BOOLEAN - Default true
created_at: TIMESTAMP WITH TIME ZONE
updated_at: TIMESTAMP WITH TIME ZONE

Indexes:
- uq_products_sku_lower: UNIQUE(lower(sku))
- ix_products_active_created: (active, created_at DESC)
```

### Webhook Model

**Table:** `webhooks`

```python
id: UUID (Primary Key)
url: VARCHAR(500) - Required
events: TEXT[] - Array of event names
is_active: BOOLEAN - Default true
secret: VARCHAR(255) - Optional (HMAC key)
description: TEXT - Optional
headers: JSONB - Custom HTTP headers
retry_count: INTEGER - Default 3
timeout_seconds: INTEGER - Default 30
last_triggered_at: TIMESTAMP - Last execution time
last_error: TEXT - Last error message
success_count: INTEGER - Total successes
failure_count: INTEGER - Total failures
created_at: TIMESTAMP WITH TIME ZONE
updated_at: TIMESTAMP WITH TIME ZONE

Indexes:
- ix_webhooks_is_active: (is_active)
```

### Webhook Log Model

**Table:** `webhook_logs`

```python
id: UUID (Primary Key)
webhook_id: UUID - Reference to webhook
event: VARCHAR(100) - Event type
payload: JSONB - Request payload
status_code: INTEGER - HTTP response code
response_body: TEXT - HTTP response
response_time_ms: INTEGER - Response time
error: TEXT - Error message if failed
created_at: TIMESTAMP WITH TIME ZONE

Indexes:
- ix_webhook_logs_webhook_id: (webhook_id)
- ix_webhook_logs_event: (event)
```

---

## API Endpoints

### Product Endpoints

**Base Path:** `/api/v1/products`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List products (paginated) |
| GET | `/{id}` | Get product by ID |
| POST | `/` | Create product |
| PUT | `/{id}` | Update product |
| DELETE | `/{id}` | Delete product |
| DELETE | `/all` | Bulk delete (Celery task) |
| POST | `/upload` | Upload CSV file |
| GET | `/upload/{task_id}/status` | Get import status |
| GET | `/delete/{task_id}/status` | Get bulk delete status |

### Webhook Endpoints

**Base Path:** `/api/v1/webhooks`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List webhooks (paginated) |
| GET | `/{id}` | Get webhook by ID |
| POST | `/` | Create webhook |
| PUT | `/{id}` | Update webhook |
| DELETE | `/{id}` | Delete webhook |
| POST | `/{id}/test` | Test webhook delivery |
| GET | `/{id}/logs` | Get execution logs |

### Celery Endpoints

**Base Path:** `/api/v1/celery`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workers` | List active workers |
| POST | `/test` | Submit test task |
| GET | `/task/{id}` | Get task status |
| DELETE | `/task/{id}` | Cancel task |

---

## CSV Import System

### Features

- Chunked reading (1,000 rows per chunk)
- Memory-efficient processing
- Case-insensitive SKU upsert
- Row-level validation
- Real-time progress tracking (Redis)
- Detailed error reporting
- Background processing (Celery)

### CSV Format

**Required Columns:**
- `sku` - Unique identifier (max 100 chars)
- `name` - Product name (max 255 chars)

**Optional Columns:**
- `description` - Product description
- `active` - Boolean (true/false, 1/0, yes/no)

**Example:**
```csv
sku,name,description,active
PROD-001,Widget Pro,Premium widget,true
PROD-002,Widget Lite,Basic widget,true
```

### Import Flow

```
1. Upload CSV → Save to /uploads
2. Trigger Celery task → process_csv_upload
3. Validate headers
4. Read in chunks (1,000 rows)
5. For each row:
   - Validate data
   - Normalize values
   - Batch upsert (ON CONFLICT UPDATE)
6. Update progress in Redis
7. Return final results
```

### Upsert Logic

```python
stmt = insert(Product).values(batch_data)
on_conflict_stmt = stmt.on_conflict_do_update(
    index_elements=[func.lower(Product.sku)],
    set_={
        "name": stmt.excluded.name,
        "description": stmt.excluded.description,
        "active": stmt.excluded.active,
        "updated_at": func.now(),
    }
)
```

### Progress Tracking

**Redis Key:** `celery-task-progress:{task_id}`

**Fields:**
- `status`: PENDING, STARTED, PROGRESS, SUCCESS, FAILURE
- `current`: Rows processed
- `total`: Total rows
- `created`: New products
- `updated`: Updated products
- `errors`: Error count
- `percent`: Progress percentage

---

## Webhook System

### Features

- HTTP POST delivery with retries
- HMAC SHA256 signature verification
- Custom headers support
- Configurable timeouts and retries
- Execution logging
- Test endpoint
- Auto-trigger on product lifecycle events

### Available Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `product.created` | Product created | id, sku, name, description, active, created_at |
| `product.updated` | Product updated | id, sku, name, description, active, updated_at |
| `product.deleted` | Product deleted | id, sku, name |
| `import.started` | CSV import starts | task_id, filename, total_rows |
| `import.completed` | CSV complete | task_id, created, updated, errors |
| `import.failed` | CSV fails | task_id, error |

### Webhook Payload Format

```json
{
  "event": "product.created",
  "timestamp": "2025-11-26T17:00:00Z",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "sku": "WIDGET-001",
    "name": "Premium Widget",
    ...
  }
}
```

### Headers Sent

```http
POST /webhook HTTP/1.1
Content-Type: application/json
User-Agent: FulFil-Webhook/1.0
X-Webhook-Event: product.created
X-Webhook-Signature: sha256=abc123... (if secret configured)
```

### HMAC Signature

```python
signature = hmac.new(
    secret.encode('utf-8'),
    payload.encode('utf-8'),
    hashlib.sha256
).hexdigest()
```

**Verification (Receiver):**
```python
def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return signature == f"sha256={expected}"
```

### Retry Logic

- Default: 3 retries
- Exponential backoff: 2^attempt seconds (2s, 4s, 8s)
- Retries on: Timeouts, network errors, non-2xx status codes
- Success: HTTP 200-299

---

## Celery Background Tasks

### Configuration

**Broker:** Redis  
**Backend:** Redis  
**Concurrency:** 2 workers  
**Task Time Limit:** 1 hour  
**Serializer:** JSON  

### Tasks

**Product Tasks:**
- `process_csv_upload` - CSV import processing
- `bulk_delete_products` - Delete all products
- `cleanup_old_imports` - Cleanup task (placeholder)

**Webhook Tasks:**
- `trigger_webhooks_for_event` - Trigger all webhooks for event
- `trigger_single_webhook` - Trigger specific webhook

### Task Discovery

```python
celery_app.conf.update(
    include=[
        "app.tasks.product_tasks",
        "app.tasks.webhook_tasks",
    ]
)
```

### Monitoring

```bash
# View active workers
docker-compose exec worker celery -A app.core.celery_app inspect active

# View stats
docker-compose exec worker celery -A app.core.celery_app inspect stats

# View logs
docker-compose logs worker -f
```

---

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```bash
# Application
APP_NAME="FulFil Product Importer"
ENVIRONMENT="development"
DEBUG=true

# Database
DATABASE_URL="postgresql+asyncpg://fulfil_user:fulfil_password@postgres:5432/fulfil_db"

# Redis
REDIS_URL="redis://redis:6379/0"

# Celery
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"

# API
API_V1_PREFIX="/api/v1"
CORS_ORIGINS=["http://localhost:5173"]
```

### Docker Compose Services

```yaml
services:
  postgres:     # PostgreSQL 15
  redis:        # Redis (broker & backend)
  backend:      # FastAPI application
  worker:       # Celery worker
```

---

## Testing

### Manual Testing

**Test CSV Import:**
```bash
curl -X POST http://localhost:8000/api/v1/products/upload \
  -F "file=@products.csv"
```

**Test Webhook:**
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/{id}/test" \
  -H "Content-Type: application/json" \
  -d '{"event":"product.created","payload":{}}'
```

**Run Test Scripts:**
```bash
# Test product CRUD
./scripts/test_crud.sh

# Test webhooks
./scripts/test_webhooks.sh
```

### Database Queries

**Product statistics:**
```sql
SELECT 
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE active = true) as active,
  COUNT(*) FILTER (WHERE active = false) as inactive
FROM products;
```

**Webhook health:**
```sql
SELECT 
  url,
  success_count,
  failure_count,
  ROUND(success_count::float / NULLIF(success_count + failure_count, 0) * 100, 2) as success_rate
FROM webhooks
WHERE is_active = true;
```

---

## Deployment

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 15
- Redis
- Python 3.11+

### Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd fulFil

# 2. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 3. Start services
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Verify
curl http://localhost:8000/api/v1/hello
```

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong database password
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure log rotation
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Set resource limits (CPU, memory)
- [ ] Configure rate limiting
- [ ] Set up health checks

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Performance

### Database

- Connection pooling via SQLAlchemy
- Async queries with asyncpg
- Proper indexes on frequently queried columns
- Case-insensitive SKU index

### CSV Import

- Chunked processing (1,000 rows)
- Batch inserts (reduces DB round-trips)
- Memory-efficient (handles 500k+ rows)
- Progress tracking via Redis

### Webhooks

- Async HTTP delivery
- Parallel webhook execution
- Connection pooling
- Configurable timeouts

### Celery

- Worker prefetch multiplier: 1
- Max tasks per child: 1,000
- Automatic task retry
- Result expiration: 1 hour

---

## Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U fulfil_user -d fulfil_db -c "SELECT 1"

# Check backend logs
docker-compose logs backend
```

### Celery Worker Issues

```bash
# Check worker is running
docker-compose ps worker

# View worker logs
docker-compose logs worker -f

# Restart worker
docker-compose restart worker
```

### Migration Issues

```bash
# Check current version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Rollback one version
docker-compose exec backend alembic downgrade -1
```

---

## Development

### Running Locally

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f backend worker

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migration
docker-compose exec backend alembic upgrade head

# Access Python shell
docker-compose exec backend python
```

### Hot Reloading

Backend has hot-reloading enabled via Uvicorn. Changes to Python files automatically restart the server.

### Database Access

```bash
# PostgreSQL shell
docker-compose exec postgres psql -U fulfil_user -d fulfil_db

# Redis CLI
docker-compose exec redis redis-cli
```

---

**Last Updated:** November 26, 2025  
**Version:** 1.0.0  
**Status:** Production Ready

