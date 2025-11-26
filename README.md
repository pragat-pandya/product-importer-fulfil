# FulFil - Product Importer

High-performance Product Importer application with async CSV processing capabilities.

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **PostgreSQL 15** - Primary database with asyncpg driver
- **SQLAlchemy 2.0** - Async ORM
- **Celery + Redis** - Background task processing
- **Python 3.11** - Runtime

### Frontend (Coming Soon)
- **React + Vite + TypeScript**
- **shadcn/ui** - UI components
- **TailwindCSS** - Styling
- **Framer Motion** - Animations
- **TanStack Query** - State management

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

3. **Access the application**
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

### Services

| Service | Port | Description |
|---------|------|-------------|
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
├── backend/              # FastAPI application
│   ├── celery_app/      # Celery worker and tasks
│   ├── config.py        # Configuration management
│   ├── main.py          # FastAPI entry point
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── docker-compose.yml   # Multi-container orchestration
├── .env                 # Environment variables
└── README.md           # This file
```

## Environment Variables

See `.env.example` for all available configuration options.

## License

Private Project

