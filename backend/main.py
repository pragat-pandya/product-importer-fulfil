"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config import settings
from app.db import get_db, close_db
from app.api.celery_routes import router as celery_router
from app.api.product_routes import router as product_router
from app.api.webhook_routes import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📦 Environment: {settings.ENVIRONMENT}")
    print(f"🗄️  Database: {str(settings.DATABASE_URL).split('@')[1] if '@' in str(settings.DATABASE_URL) else 'configured'}")
    print(f"🔴 Redis: {str(settings.REDIS_URL).split('@')[1] if '@' in str(settings.REDIS_URL) else 'configured'}")
    
    yield
    
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")
    await close_db()


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="High-performance Product Importer with async CSV processing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(celery_router, prefix=settings.API_V1_PREFIX)
app.include_router(product_router, prefix=settings.API_V1_PREFIX)
app.include_router(webhook_router, prefix=settings.API_V1_PREFIX)


# Health Check Endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status check"""
    return JSONResponse(
        content={
            "status": "running",
            "service": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "message": "Welcome to FulFil Product Importer API! 🚀",
        }
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
        }
    )


@app.get(f"{settings.API_V1_PREFIX}/hello", tags=["Demo"])
async def hello_world(db: AsyncSession = Depends(get_db)):
    """Demo hello-world endpoint with database connectivity check"""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "connected" if result else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JSONResponse(
        content={
            "message": "Hello from FulFil! 👋",
            "database": db_status,
            "redis": "connected" if settings.REDIS_URL else "not configured",
        }
    )
