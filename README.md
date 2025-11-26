# FulFil - Product Importer

High-performance product import system with CSV processing, webhooks, and real-time progress tracking.

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- PostgreSQL 15 (handled by Docker)
- Redis (handled by Docker)

### Run Application

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Features

### Core Functionality

- **CSV Import:** Bulk product import with chunked processing (1,000 rows/chunk)
- **Product CRUD:** Complete product lifecycle management
- **Webhooks:** Event-driven notifications with HMAC signatures
- **Real-time Progress:** Live import progress tracking via Redis
- **Background Tasks:** Celery-powered async processing

### Technical Highlights

- **FastAPI:** Modern async Python web framework
- **React + TypeScript:** Type-safe frontend with Vite
- **PostgreSQL 15:** Async database with case-insensitive SKU indexing
- **SQLAlchemy 2.0:** Async ORM with proper relationships
- **Celery + Redis:** Distributed task queue
- **Framer Motion:** Smooth page transitions
- **TanStack Query:** Efficient server state management
- **shadcn/ui:** Beautiful, accessible UI components

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI   │────▶│ PostgreSQL  │
│    React    │     │   Backend   │     │     DB      │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ├────▶ ┌─────────────┐
                           │      │    Redis    │
                           │      │   Broker    │
                           │      └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Celery    │
                    │   Workers   │
                    └─────────────┘
```

---

## Project Structure

```
fulFil/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # Routes (Controllers)
│   │   ├── services/        # Business Logic
│   │   ├── repositories/    # Data Access Layer
│   │   ├── models/          # SQLAlchemy Models
│   │   ├── schemas/         # Pydantic Schemas
│   │   ├── tasks/           # Celery Tasks
│   │   ├── core/            # Core Configuration
│   │   └── db/              # Database Setup
│   ├── alembic/             # Database Migrations
│   ├── main.py              # Application Entry
│   ├── config.py            # Settings
│   └── requirements.txt     # Python Dependencies
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # Reusable Components
│   │   ├── pages/           # Page Components
│   │   ├── hooks/           # Custom Hooks
│   │   ├── types/           # TypeScript Types
│   │   └── lib/             # Utilities
│   ├── package.json         # Node Dependencies
│   └── vite.config.ts       # Vite Configuration
├── docker-compose.yml       # Service Orchestration
├── BACKEND_DOCS.md          # Backend Documentation
└── FRONTEND_DOCS.md         # Frontend Documentation
```

---

## API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products (paginated) |
| POST | `/api/v1/products` | Create product |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product |
| DELETE | `/api/v1/products/all` | Bulk delete |
| POST | `/api/v1/products/upload` | Upload CSV |
| GET | `/api/v1/products/upload/{task_id}/status` | Import status |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/webhooks` | List webhooks |
| POST | `/api/v1/webhooks` | Create webhook |
| PUT | `/api/v1/webhooks/{id}` | Update webhook |
| DELETE | `/api/v1/webhooks/{id}` | Delete webhook |
| POST | `/api/v1/webhooks/{id}/test` | Test webhook |
| GET | `/api/v1/webhooks/{id}/logs` | Execution logs |

---

## CSV Import Format

### Required Columns

- `sku` - Unique identifier (max 100 chars, case-insensitive)
- `name` - Product name (max 255 chars)

### Optional Columns

- `description` - Product description
- `active` - Boolean (true/false, 1/0, yes/no)

### Example CSV

```csv
sku,name,description,active
PROD-001,Widget Pro,Premium widget,true
PROD-002,Widget Lite,Basic widget,true
PROD-003,Widget Max,Maximum performance widget,false
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

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

---

## Development

### Backend Development

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# View logs
docker-compose logs backend -f
docker-compose logs worker -f

# Access database
docker-compose exec postgres psql -U fulfil_user -d fulfil_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Testing

### Manual API Testing

```bash
# Test API health
curl http://localhost:8000/api/v1/hello

# Upload CSV
curl -X POST http://localhost:8000/api/v1/products/upload \
  -F "file=@products.csv"

# List products
curl http://localhost:8000/api/v1/products

# Create webhook
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{"url":"https://webhook.site/...", "events":["product.created"]}'
```

### Test Scripts

```bash
# Test product CRUD
./scripts/test_crud.sh

# Test webhooks
./scripts/test_webhooks.sh
```

---

## Documentation

Comprehensive documentation available:

- **Backend:** [BACKEND_DOCS.md](./BACKEND_DOCS.md)
  - Architecture, API, database models, Celery tasks, webhooks
- **Frontend:** [FRONTEND_DOCS.md](./FRONTEND_DOCS.md)
  - Components, state management, styling, deployment
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

---

## Troubleshooting

### Database Connection Issues

```bash
docker-compose ps postgres
docker-compose logs postgres
docker-compose restart postgres
```

### Celery Worker Issues

```bash
docker-compose ps worker
docker-compose logs worker -f
docker-compose restart worker
```

### Frontend Build Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Production Deployment

### Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Configure strong database password
- [ ] Set production `CORS_ORIGINS`
- [ ] Enable SSL/TLS certificates
- [ ] Configure log aggregation
- [ ] Set up database backups
- [ ] Configure monitoring (Sentry, etc.)
- [ ] Set resource limits (CPU, memory)
- [ ] Enable rate limiting
- [ ] Configure CDN for static assets

### Build Commands

```bash
# Backend
docker build -t fulfil-backend ./backend

# Frontend
cd frontend && npm run build

# Deploy dist/ folder to CDN/static hosting
```

---

## Tech Stack Summary

### Backend

- Python 3.11
- FastAPI 0.104+
- SQLAlchemy 2.0 (Async)
- PostgreSQL 15
- Celery 5.3
- Redis
- Alembic
- Pydantic v2
- httpx

### Frontend

- React 19
- TypeScript 5.9
- Vite 7.2
- TailwindCSS 3.4
- shadcn/ui
- TanStack Query v5
- Framer Motion 12
- React Router DOM v7
- Axios

### Infrastructure

- Docker & Docker Compose
- Nginx (production)
- PostgreSQL 15
- Redis

---

## Performance

- **CSV Import:** Handles 500k+ rows efficiently
- **API Response:** < 100ms average
- **Database:** Indexed for fast lookups
- **Frontend:** 242 KB gzipped bundle
- **Animations:** 60 FPS smooth transitions

---

## License

MIT License

---

## Support

For issues or questions:
- Check documentation: [BACKEND_DOCS.md](./BACKEND_DOCS.md) | [FRONTEND_DOCS.md](./FRONTEND_DOCS.md)
- Review API docs: http://localhost:8000/docs
- Check logs: `docker-compose logs -f`

---

**Version:** 1.0.0  
**Last Updated:** November 26, 2025  
**Status:** Production Ready
