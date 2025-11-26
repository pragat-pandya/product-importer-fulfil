"""
Application Configuration using Pydantic Settings
"""
import json
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application Settings
    APP_NAME: str = Field(default="FulFil Product Importer", description="Application name")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Database Settings
    DATABASE_URL: PostgresDsn = Field(
        description="PostgreSQL database URL with asyncpg driver"
    )
    
    # Redis Settings
    REDIS_URL: RedisDsn = Field(
        description="Redis URL for Celery broker and result backend"
    )
    
    # API Settings
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version 1 prefix")
    
    # CORS Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from JSON string or comma-separated string"""
        if isinstance(v, str):
            # Try parsing as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, try comma-separated
                if ',' in v:
                    return [origin.strip() for origin in v.split(',')]
                # Single value
                return [v.strip()]
        return v
    
    # Celery Settings
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-populate Celery URLs from Redis URL if not set
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = str(self.REDIS_URL)
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = str(self.REDIS_URL)
    
    @property
    def database_url_sync(self) -> str:
        """Convert async database URL to sync for Alembic migrations"""
        return str(self.DATABASE_URL).replace("+asyncpg", "")


# Global settings instance
settings = Settings()

