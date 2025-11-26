# FulFil - Product Importer

High-performance Product Importer application with async CSV processing capabilities.

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **PostgreSQL 15** - Primary database with asyncpg driver
- **SQLAlchemy 2.0** - Async ORM
- **Celery + Redis** - Background task processing
- **Python 3.11** - Runtime

### Frontend
- **React 19 + Vite + TypeScript** - Modern build tooling
- **shadcn/ui** - Beautiful UI components
- **TailwindCSS 3** - Utility-first styling
- **Framer Motion** - Smooth animations
- **TanStack Query v5** - Server state management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Getting Started

### Prerequisites
- Docker Desktop installed
- Docker Compose v3.8+

### Quick Start

1. **Clone and setup**
```bash
cd fulFil
cp .env.example .env
```

2. **Start all services**
```bash
docker-compose up
```

3. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

## Features

### ✅ Completed

#### Database Layer
- SQLAlchemy 2.0 with async support
- PostgreSQL 15 with asyncpg driver
- Product model with case-insensitive unique SKU
- Alembic migrations configured

#### Celery Background Tasks
- Celery worker running in Docker
- Redis as broker and result backend
- Task auto-discovery from `app/tasks/`
- API endpoints for task management:
  - `GET /api/v1/celery/workers` - View active workers
  - `POST /api/v1/celery/test` - Submit test task
  - `GET /api/v1/celery/task/{id}` - Check task status
  - `DELETE /api/v1/celery/task/{id}` - Cancel task

See [CELERY_SETUP.md](./CELERY_SETUP.md) for detailed Celery documentation.

#### CSV Product Import
- Async CSV processing with Celery
- Memory-efficient chunked reading (handles 500k+ rows)
- Case-insensitive SKU upsert logic
- Real-time progress tracking via Redis
- Row-level validation and error reporting
- API endpoints:
  - `POST /api/v1/products/upload` - Upload CSV file
  - `GET /api/v1/products/upload/{id}/status` - Check status (simplified)
  - `GET /api/v1/products/import/{id}/progress` - Check progress (detailed)
  - `GET /api/v1/products/import/{id}/result` - Get final results

See [CSV_IMPORT_GUIDE.md](./CSV_IMPORT_GUIDE.md) for detailed CSV import documentation.

#### Frontend Upload Interface
- Drag-and-drop file upload with react-dropzone
- Real-time progress tracking (1-second polling)
- Animated progress bar with Framer Motion
- Status badges and toast notifications
- File validation (CSV only, max 100MB)
- Stats display (Created/Updated/Errors)

See [UPLOAD_FEATURE.md](./UPLOAD_FEATURE.md) for detailed upload UI documentation.

### Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 5173 | React application (dev) |
| Backend | 8000 | FastAPI application |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Celery broker |
| Worker | - | Celery worker |

### Development

The backend has hot-reload enabled. Any changes to Python files will automatically restart the server.

### Docker Commands

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Rebuild containers
docker-compose up --build

# Clean everything (including volumes)
docker-compose down -v
```

## Architecture

```
fulFil/
├── frontend/                # React application
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # Utilities & API
│   │   ├── App.tsx         # Main app
│   │   └── main.tsx        # Entry point
│   ├── tailwind.config.js  # Tailwind config
│   ├── vite.config.ts      # Vite config
│   └── package.json        # Node dependencies
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core components
│   │   ├── db/             # Database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Celery tasks
│   ├── alembic/            # Database migrations
│   ├── config.py           # Configuration
│   ├── main.py             # FastAPI entry point
│   ├── Dockerfile          # Backend container
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Multi-container orchestration
├── .env                    # Environment variables
└── README.md              # This file
```

## API Endpoints

### Product CRUD

Full CRUD operations for products with pagination, filtering, and bulk operations.

| Method | Endpoint                            | Description                          |
|--------|-------------------------------------|--------------------------------------|
| GET    | `/products`                         | List products (paginated, filtered)  |
| GET    | `/products/{id}`                    | Get product by ID                    |
| POST   | `/products`                         | Create a new product                 |
| PUT    | `/products/{id}`                    | Update a product                     |
| DELETE | `/products/{id}`                    | Delete a product                     |
| DELETE | `/products/all`                     | Bulk delete (Celery task)            |
| GET    | `/products/delete/{task_id}/status` | Check bulk delete status             |

**Features:**
- ✅ Pagination with `limit` and `offset`
- ✅ Filtering by `sku`, `name`, `active`
- ✅ Case-insensitive SKU uniqueness
- ✅ Background bulk delete via Celery

See [CRUD_ENDPOINTS.md](./CRUD_ENDPOINTS.md) for complete API documentation.

### CSV Import

| Method | Endpoint                              | Description                    |
|--------|---------------------------------------|--------------------------------|
| POST   | `/products/upload`                    | Upload CSV file                |
| GET    | `/products/upload/{task_id}/status`   | Get import status (polling)    |
| GET    | `/products/import/{task_id}/progress` | Get detailed progress          |
| GET    | `/products/import/{task_id}/result`   | Get final import results       |

**Features:**
- ✅ Chunked CSV processing (1000 rows/chunk)
- ✅ Case-insensitive SKU upsert
- ✅ Real-time progress tracking via Redis
- ✅ Background processing via Celery
- ✅ Detailed error reporting

### Webhook System

| Method | Endpoint                              | Description                    |
|--------|---------------------------------------|--------------------------------|
| GET    | `/webhooks`                           | List webhooks (paginated)      |
| GET    | `/webhooks/{id}`                      | Get webhook by ID              |
| POST   | `/webhooks`                           | Create webhook                 |
| PUT    | `/webhooks/{id}`                      | Update webhook                 |
| DELETE | `/webhooks/{id}`                      | Delete webhook                 |
| POST   | `/webhooks/{id}/test`                 | Test webhook delivery          |
| GET    | `/webhooks/{id}/logs`                 | Get execution logs             |

**Features:**
- ✅ HTTP delivery with retry logic
- ✅ HMAC SHA256 signature verification
- ✅ Custom headers support
- ✅ Execution logging and monitoring
- ✅ Test endpoint with response time
- ✅ Auto-trigger on product lifecycle events
- ✅ Background execution via Celery
- ✅ Configurable timeouts and retries

**Events:**
- `product.created`, `product.updated`, `product.deleted`
- `import.started`, `import.completed`, `import.failed`

See [WEBHOOK_SYSTEM.md](./WEBHOOK_SYSTEM.md) for complete webhook documentation.

### Testing

Run the comprehensive test suite:

```bash
# Test CRUD endpoints
./scripts/test_crud.sh

# Verify services
docker-compose ps
curl http://localhost:8000/api/v1/hello | jq '.'
```

### Interactive API Documentation

FastAPI provides auto-generated interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all available configuration options.

## License

Private Project

