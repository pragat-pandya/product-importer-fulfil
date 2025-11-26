"""
Webhook Service - Business Logic Layer
Handles webhook triggering and HTTP delivery logic.
"""
import hmac
import hashlib
import json
import time
from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.webhook_repository import WebhookRepository
from app.schemas.webhook_schema import WebhookCreate, WebhookUpdate
from app.models.webhook import Webhook, WebhookLog


class WebhookService:
    """Service for Webhook business logic and HTTP delivery."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = WebhookRepository(db_session)
    
    async def get_webhook_by_id(self, webhook_id: UUID) -> Webhook:
        """
        Get a webhook by ID.
        
        Raises:
            HTTPException: If webhook not found.
        """
        webhook = await self.repository.get_by_id(webhook_id)
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook with ID {webhook_id} not found"
            )
        return webhook
    
    async def get_webhooks(
        self,
        limit: int = 20,
        offset: int = 0,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Webhook], int]:
        """Get all webhooks with pagination and optional filtering."""
        webhooks, total = await self.repository.get_all(
            limit=limit,
            offset=offset,
            is_active=is_active,
        )
        return webhooks, total
    
    async def create_webhook(self, webhook_data: WebhookCreate) -> Webhook:
        """Create a new webhook."""
        webhook = await self.repository.create(webhook_data)
        return webhook
    
    async def update_webhook(self, webhook_id: UUID, webhook_data: WebhookUpdate) -> Webhook:
        """Update an existing webhook."""
        webhook = await self.get_webhook_by_id(webhook_id)
        updated_webhook = await self.repository.update(webhook, webhook_data)
        return updated_webhook
    
    async def delete_webhook(self, webhook_id: UUID) -> None:
        """Delete a webhook."""
        webhook = await self.get_webhook_by_id(webhook_id)
        await self.repository.delete(webhook)
    
    async def get_webhook_logs(
        self,
        webhook_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookLog], int]:
        """Get execution logs for a webhook."""
        # Verify webhook exists
        await self.get_webhook_by_id(webhook_id)
        logs, total = await self.repository.get_logs(webhook_id, limit, offset)
        return logs, total
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC SHA256 signature for payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def trigger_webhook(
        self,
        webhook: Webhook,
        event: str,
        payload: Dict[str, Any],
    ) -> Tuple[bool, Optional[int], Optional[str], int]:
        """
        Trigger a webhook by sending HTTP POST request.
        
        Args:
            webhook: Webhook to trigger
            event: Event type
            payload: Data to send
            
        Returns:
            Tuple of (success, status_code, response_body, response_time_ms)
        """
        start_time = time.time()
        
        # Prepare payload
        webhook_payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload,
        }
        payload_json = json.dumps(webhook_payload)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FulFil-Webhook/1.0",
            "X-Webhook-Event": event,
        }
        
        # Add custom headers
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Add signature if secret is configured
        if webhook.secret:
            signature = self._generate_signature(payload_json, webhook.secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        # Attempt delivery with retries
        last_error = None
        status_code = None
        response_body = None
        
        for attempt in range(webhook.retry_count + 1):
            try:
                async with httpx.AsyncClient(timeout=webhook.timeout_seconds) as client:
                    response = await client.post(
                        webhook.url,
                        content=payload_json,
                        headers=headers,
                    )
                    
                    status_code = response.status_code
                    response_body = response.text[:1000]  # Limit to 1000 chars
                    
                    # Consider 2xx status codes as success
                    if 200 <= status_code < 300:
                        response_time_ms = int((time.time() - start_time) * 1000)
                        return True, status_code, response_body, response_time_ms
                    else:
                        last_error = f"HTTP {status_code}: {response_body}"
                        
            except httpx.TimeoutException:
                last_error = f"Request timeout after {webhook.timeout_seconds}s"
            except httpx.RequestError as e:
                last_error = f"Request error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
            
            # Don't retry on last attempt
            if attempt < webhook.retry_count:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        response_time_ms = int((time.time() - start_time) * 1000)
        return False, status_code, last_error, response_time_ms
    
    async def execute_webhook(
        self,
        webhook_id: UUID,
        event: str,
        payload: Dict[str, Any],
    ) -> WebhookLog:
        """
        Execute a webhook and log the result.
        
        This is the main entry point for triggering webhooks.
        """
        webhook = await self.get_webhook_by_id(webhook_id)
        
        # Check if webhook is active
        if not webhook.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook is not active"
            )
        
        # Check if webhook subscribes to this event
        if event not in webhook.events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook does not subscribe to event '{event}'"
            )
        
        # Trigger webhook
        success, status_code, response_body, response_time_ms = await self.trigger_webhook(
            webhook, event, payload
        )
        
        # Update webhook stats
        await self.repository.update_stats(
            webhook,
            success=success,
            last_triggered_at=datetime.utcnow(),
            last_error=None if success else response_body,
        )
        
        # Create log entry
        log = await self.repository.create_log(
            webhook_id=webhook.id,
            event=event,
            payload=payload,
            status_code=status_code,
            response_body=response_body,
            response_time_ms=response_time_ms,
            error=None if success else response_body,
        )
        
        return log
    
    async def test_webhook(
        self,
        webhook_id: UUID,
        event: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Test a webhook by sending a test payload.
        
        Returns:
            Dict with test results including status code and response time.
        """
        webhook = await self.get_webhook_by_id(webhook_id)
        
        # Use provided payload or generate a test payload
        if payload is None:
            payload = {
                "test": True,
                "message": "This is a test webhook delivery",
                "webhook_id": str(webhook.id),
            }
        
        # Trigger webhook
        success, status_code, response_body, response_time_ms = await self.trigger_webhook(
            webhook, event, payload
        )
        
        # Create log entry for test
        await self.repository.create_log(
            webhook_id=webhook.id,
            event=event,
            payload=payload,
            status_code=status_code,
            response_body=response_body,
            response_time_ms=response_time_ms,
            error=None if success else response_body,
        )
        
        return {
            "success": success,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "response_body": response_body,
            "error": None if success else response_body,
        }
    
    async def trigger_event(
        self,
        event: str,
        payload: Dict[str, Any],
    ) -> int:
        """
        Trigger all active webhooks for a specific event.
        
        This is called from the application when events occur.
        Returns the number of webhooks triggered.
        """
        webhooks = await self.repository.get_active_by_event(event)
        
        triggered_count = 0
        for webhook in webhooks:
            try:
                await self.execute_webhook(webhook.id, event, payload)
                triggered_count += 1
            except Exception as e:
                # Log error but continue with other webhooks
                pass
        
        return triggered_count


# Import asyncio at the top if not already
import asyncio

