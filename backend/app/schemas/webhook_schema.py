"""
Webhook Pydantic Schemas for Request/Response Validation
"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator


class WebhookBase(BaseModel):
    """Base Webhook schema with common fields."""
    
    url: str = Field(..., description="Target URL for webhook delivery")
    events: List[str] = Field(..., min_length=1, description="List of events to subscribe to")
    is_active: bool = Field(default=True, description="Whether webhook is currently active")
    secret: Optional[str] = Field(None, max_length=255, description="Secret key for HMAC signature")
    description: Optional[str] = Field(None, description="Human-readable description")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom HTTP headers")
    retry_count: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        if len(v) > 500:
            raise ValueError('URL must be less than 500 characters')
        return v

    @field_validator('events')
    @classmethod
    def validate_events(cls, v: List[str]) -> List[str]:
        """Validate event names"""
        valid_events = {
            'product.created',
            'product.updated',
            'product.deleted',
            'import.started',
            'import.completed',
            'import.failed',
        }
        for event in v:
            if event not in valid_events:
                raise ValueError(
                    f"Invalid event '{event}'. "
                    f"Valid events: {', '.join(sorted(valid_events))}"
                )
        return v


class WebhookCreate(WebhookBase):
    """Schema for creating a new webhook."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/webhook",
                "events": ["product.created", "product.updated"],
                "is_active": True,
                "secret": "my-secret-key",
                "description": "Webhook for product updates",
                "headers": {"X-Custom-Header": "value"},
                "retry_count": 3,
                "timeout_seconds": 30,
            }
        }
    )


class WebhookUpdate(BaseModel):
    """Schema for updating an existing webhook."""
    
    url: Optional[str] = Field(None, description="Target URL for webhook delivery")
    events: Optional[List[str]] = Field(None, min_length=1, description="List of events")
    is_active: Optional[bool] = Field(None, description="Whether webhook is active")
    secret: Optional[str] = Field(None, max_length=255, description="Secret key")
    description: Optional[str] = Field(None, description="Description")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    retry_count: Optional[int] = Field(None, ge=0, le=10, description="Retry attempts")
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300, description="Timeout")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format"""
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError('URL must start with http:// or https://')
            if len(v) > 500:
                raise ValueError('URL must be less than 500 characters')
        return v

    @field_validator('events')
    @classmethod
    def validate_events(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate event names"""
        if v is not None:
            valid_events = {
                'product.created',
                'product.updated',
                'product.deleted',
                'import.started',
                'import.completed',
                'import.failed',
            }
            for event in v:
                if event not in valid_events:
                    raise ValueError(
                        f"Invalid event '{event}'. "
                        f"Valid events: {', '.join(sorted(valid_events))}"
                    )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/webhook",
                "is_active": False,
            }
        }
    )


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    
    id: UUID = Field(..., description="Webhook unique identifier")
    last_triggered_at: Optional[datetime] = Field(None, description="Last trigger timestamp")
    last_error: Optional[str] = Field(None, description="Last error message")
    success_count: int = Field(..., description="Total successful deliveries")
    failure_count: int = Field(..., description="Total failed deliveries")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "https://example.com/webhook",
                "events": ["product.created", "product.updated"],
                "is_active": True,
                "secret": "my-secret-key",
                "description": "Webhook for product updates",
                "headers": {"X-Custom-Header": "value"},
                "retry_count": 3,
                "timeout_seconds": 30,
                "last_triggered_at": "2025-11-26T15:00:00Z",
                "last_error": None,
                "success_count": 42,
                "failure_count": 2,
                "created_at": "2025-11-26T15:00:00Z",
                "updated_at": "2025-11-26T15:00:00Z",
            }
        }
    )


class WebhookListResponse(BaseModel):
    """Schema for paginated webhook list response."""
    
    items: List[WebhookResponse] = Field(..., description="List of webhooks")
    total: int = Field(..., description="Total number of webhooks")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether there are more items")


class WebhookTestRequest(BaseModel):
    """Schema for testing a webhook."""
    
    event: str = Field(..., description="Event type to test")
    payload: Optional[Dict] = Field(None, description="Custom test payload")

    @field_validator('event')
    @classmethod
    def validate_event(cls, v: str) -> str:
        """Validate event name"""
        valid_events = {
            'product.created',
            'product.updated',
            'product.deleted',
            'import.started',
            'import.completed',
            'import.failed',
        }
        if v not in valid_events:
            raise ValueError(
                f"Invalid event '{v}'. "
                f"Valid events: {', '.join(sorted(valid_events))}"
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event": "product.created",
                "payload": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "sku": "TEST-001",
                    "name": "Test Product",
                },
            }
        }
    )


class WebhookTestResponse(BaseModel):
    """Schema for webhook test response."""
    
    success: bool = Field(..., description="Whether test was successful")
    status_code: Optional[int] = Field(None, description="HTTP response status code")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    response_body: Optional[str] = Field(None, description="HTTP response body")
    error: Optional[str] = Field(None, description="Error message if failed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "status_code": 200,
                "response_time_ms": 145,
                "response_body": '{"status": "ok"}',
                "error": None,
            }
        }
    )


class WebhookLogResponse(BaseModel):
    """Schema for webhook log response."""
    
    id: UUID = Field(..., description="Log unique identifier")
    webhook_id: UUID = Field(..., description="Webhook ID")
    event: str = Field(..., description="Event type")
    payload: Dict = Field(..., description="Request payload")
    status_code: Optional[int] = Field(None, description="HTTP response status code")
    response_body: Optional[str] = Field(None, description="HTTP response body")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Execution timestamp")

    model_config = ConfigDict(from_attributes=True)

