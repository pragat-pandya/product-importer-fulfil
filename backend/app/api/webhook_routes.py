"""
Webhook API Routes
Complete CRUD operations for webhooks with testing functionality
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.webhook_service import WebhookService
from app.schemas.webhook_schema import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookListResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookLogResponse,
)


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.get("", response_model=WebhookListResponse, summary="List Webhooks")
async def list_webhooks(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    db_session: AsyncSession = Depends(get_db),
) -> WebhookListResponse:
    """
    Get a paginated list of webhooks with optional filtering.
    
    **Features:**
    - Pagination with limit and offset
    - Filter by active status
    - Ordered by creation date (newest first)
    
    **Example:**
    ```
    GET /webhooks?limit=10&is_active=true
    ```
    """
    service = WebhookService(db_session)
    
    webhooks, total = await service.get_webhooks(
        limit=limit,
        offset=offset,
        is_active=is_active,
    )
    
    webhook_responses = [WebhookResponse.model_validate(w) for w in webhooks]
    
    return WebhookListResponse(
        items=webhook_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.post("", response_model=WebhookResponse, status_code=201, summary="Create Webhook")
async def create_webhook(
    webhook_data: WebhookCreate,
    db_session: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """
    Create a new webhook.
    
    **Required Fields:**
    - `url`: Target URL (must start with http:// or https://)
    - `events`: List of events to subscribe to
    
    **Valid Events:**
    - `product.created` - Triggered when a product is created
    - `product.updated` - Triggered when a product is updated
    - `product.deleted` - Triggered when a product is deleted
    - `import.started` - Triggered when CSV import starts
    - `import.completed` - Triggered when CSV import completes
    - `import.failed` - Triggered when CSV import fails
    
    **Optional Fields:**
    - `secret`: Secret key for HMAC SHA256 signature verification
    - `headers`: Custom HTTP headers (JSON object)
    - `retry_count`: Number of retry attempts (0-10, default: 3)
    - `timeout_seconds`: Request timeout (1-300, default: 30)
    
    **Example:**
    ```json
    {
      "url": "https://example.com/webhook",
      "events": ["product.created", "product.updated"],
      "secret": "my-secret-key",
      "description": "Product updates webhook",
      "is_active": true
    }
    ```
    """
    service = WebhookService(db_session)
    webhook = await service.create_webhook(webhook_data)
    return WebhookResponse.model_validate(webhook)


@router.get("/{webhook_id}", response_model=WebhookResponse, summary="Get Webhook by ID")
async def get_webhook(
    webhook_id: UUID,
    db_session: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """
    Get a single webhook by its ID.
    
    **Returns:**
    - Webhook details including statistics (success/failure counts)
    - Last trigger timestamp and error (if any)
    
    **Example:**
    ```
    GET /webhooks/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    service = WebhookService(db_session)
    webhook = await service.get_webhook_by_id(webhook_id)
    return WebhookResponse.model_validate(webhook)


@router.put("/{webhook_id}", response_model=WebhookResponse, summary="Update Webhook")
async def update_webhook(
    webhook_id: UUID,
    webhook_data: WebhookUpdate,
    db_session: AsyncSession = Depends(get_db),
) -> WebhookResponse:
    """
    Update an existing webhook.
    
    **Supports partial updates** - only send fields you want to change.
    
    **Example:**
    ```json
    {
      "is_active": false,
      "description": "Temporarily disabled"
    }
    ```
    """
    service = WebhookService(db_session)
    webhook = await service.update_webhook(webhook_id, webhook_data)
    return WebhookResponse.model_validate(webhook)


@router.delete("/{webhook_id}", status_code=204, summary="Delete Webhook")
async def delete_webhook(
    webhook_id: UUID,
    db_session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a webhook.
    
    **Note:** Associated logs will remain in the database for audit purposes.
    
    **Example:**
    ```
    DELETE /webhooks/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    service = WebhookService(db_session)
    await service.delete_webhook(webhook_id)


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    summary="Test Webhook"
)
async def test_webhook(
    webhook_id: UUID,
    test_request: WebhookTestRequest,
    db_session: AsyncSession = Depends(get_db),
) -> WebhookTestResponse:
    """
    Test a webhook by sending a dummy payload.
    
    **Features:**
    - Sends real HTTP request to the webhook URL
    - Returns status code and response time
    - Logs the test execution
    - Does not require webhook to be active
    
    **Request Body:**
    ```json
    {
      "event": "product.created",
      "payload": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "sku": "TEST-001",
        "name": "Test Product"
      }
    }
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "status_code": 200,
      "response_time_ms": 145,
      "response_body": "{\"status\": \"ok\"}",
      "error": null
    }
    ```
    
    **Use Cases:**
    - Verify webhook URL is accessible
    - Test authentication and authorization
    - Measure response time
    - Debug webhook integration
    """
    service = WebhookService(db_session)
    
    result = await service.test_webhook(
        webhook_id=webhook_id,
        event=test_request.event,
        payload=test_request.payload,
    )
    
    return WebhookTestResponse(**result)


@router.get(
    "/{webhook_id}/logs",
    response_model=List[WebhookLogResponse],
    summary="Get Webhook Logs"
)
async def get_webhook_logs(
    webhook_id: UUID,
    limit: int = Query(default=50, ge=1, le=100, description="Number of logs to return"),
    offset: int = Query(default=0, ge=0, description="Number of logs to skip"),
    db_session: AsyncSession = Depends(get_db),
) -> List[WebhookLogResponse]:
    """
    Get execution logs for a webhook.
    
    **Features:**
    - View webhook delivery history
    - Debug failed deliveries
    - Monitor performance (response times)
    - Ordered by execution time (newest first)
    
    **Response includes:**
    - Event type
    - Payload sent
    - HTTP status code
    - Response body (truncated to 1000 chars)
    - Response time in milliseconds
    - Error message (if failed)
    
    **Example:**
    ```
    GET /webhooks/123e4567-e89b-12d3-a456-426614174000/logs?limit=20
    ```
    """
    service = WebhookService(db_session)
    logs, total = await service.get_webhook_logs(webhook_id, limit, offset)
    return [WebhookLogResponse.model_validate(log) for log in logs]

