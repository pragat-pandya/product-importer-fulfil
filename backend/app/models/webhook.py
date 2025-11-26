"""
Webhook Model
Stores webhook configurations for external integrations
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, Boolean, DateTime, func, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.db.base import Base


class WebhookEvent(str, enum.Enum):
    """Enum for webhook event types"""
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    IMPORT_STARTED = "import.started"
    IMPORT_COMPLETED = "import.completed"
    IMPORT_FAILED = "import.failed"


class Webhook(Base):
    """
    Webhook model for external integrations.
    
    Attributes:
        id: Unique identifier
        url: Target URL for webhook delivery
        events: List of events to trigger on
        is_active: Whether webhook is currently active
        secret: Secret key for HMAC signature (optional)
        description: Human-readable description
        headers: Custom HTTP headers (JSON)
        retry_count: Number of times to retry on failure
        timeout_seconds: Request timeout in seconds
        last_triggered_at: Last successful trigger timestamp
        last_error: Last error message (if any)
        success_count: Total successful deliveries
        failure_count: Total failed deliveries
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "webhooks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=3)
    timeout_seconds: Mapped[int] = mapped_column(default=30)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success_count: Mapped[int] = mapped_column(default=0)
    failure_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, url={self.url}, active={self.is_active})>"


class WebhookLog(Base):
    """
    Webhook execution log for debugging and monitoring.
    
    Attributes:
        id: Unique identifier
        webhook_id: Reference to webhook
        event: Event that triggered the webhook
        payload: Request payload (JSON)
        status_code: HTTP response status code
        response_body: HTTP response body
        response_time_ms: Response time in milliseconds
        error: Error message (if failed)
        created_at: Execution timestamp
    """
    __tablename__ = "webhook_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    webhook_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<WebhookLog(id={self.id}, webhook_id={self.webhook_id}, event={self.event})>"

