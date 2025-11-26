"""
Webhook Repository - Data Access Layer
Handles all database operations for Webhook and WebhookLog models.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.webhook import Webhook, WebhookLog
from app.schemas.webhook_schema import WebhookCreate, WebhookUpdate


class WebhookRepository:
    """Repository for Webhook CRUD operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_by_id(self, webhook_id: UUID) -> Optional[Webhook]:
        """Get a webhook by ID."""
        result = await self.db_session.execute(
            select(Webhook).where(Webhook.id == webhook_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Webhook], int]:
        """
        Get all webhooks with pagination and optional filtering.
        
        Returns:
            Tuple of (webhooks_list, total_count)
        """
        query = select(Webhook)
        count_query = select(func.count()).select_from(Webhook)
        
        # Apply filters
        if is_active is not None:
            query = query.where(Webhook.is_active == is_active)
            count_query = count_query.where(Webhook.is_active == is_active)
        
        # Apply ordering and pagination
        query = query.order_by(desc(Webhook.created_at)).limit(limit).offset(offset)
        
        # Execute queries
        result = await self.db_session.execute(query)
        webhooks = list(result.scalars().all())
        
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar()
        
        return webhooks, total
    
    async def get_active_by_event(self, event: str) -> List[Webhook]:
        """Get all active webhooks that subscribe to a specific event."""
        result = await self.db_session.execute(
            select(Webhook)
            .where(Webhook.is_active == True)
            .where(Webhook.events.contains([event]))
        )
        return list(result.scalars().all())
    
    async def create(self, webhook_data: WebhookCreate) -> Webhook:
        """Create a new webhook."""
        webhook = Webhook(
            url=webhook_data.url,
            events=webhook_data.events,
            is_active=webhook_data.is_active,
            secret=webhook_data.secret,
            description=webhook_data.description,
            headers=webhook_data.headers,
            retry_count=webhook_data.retry_count,
            timeout_seconds=webhook_data.timeout_seconds,
        )
        self.db_session.add(webhook)
        await self.db_session.flush()
        await self.db_session.refresh(webhook)
        return webhook
    
    async def update(self, webhook: Webhook, webhook_data: WebhookUpdate) -> Webhook:
        """Update an existing webhook."""
        update_data = webhook_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(webhook, field, value)
        
        await self.db_session.flush()
        await self.db_session.refresh(webhook)
        return webhook
    
    async def delete(self, webhook: Webhook) -> None:
        """Delete a webhook."""
        await self.db_session.delete(webhook)
        await self.db_session.flush()
    
    async def update_stats(
        self,
        webhook: Webhook,
        success: bool,
        last_triggered_at,
        last_error: Optional[str] = None,
    ) -> None:
        """Update webhook statistics after execution."""
        if success:
            webhook.success_count += 1
            webhook.last_error = None
        else:
            webhook.failure_count += 1
            webhook.last_error = last_error
        
        webhook.last_triggered_at = last_triggered_at
        await self.db_session.flush()
    
    async def create_log(
        self,
        webhook_id: UUID,
        event: str,
        payload: dict,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> WebhookLog:
        """Create a webhook execution log."""
        log = WebhookLog(
            webhook_id=webhook_id,
            event=event,
            payload=payload,
            status_code=status_code,
            response_body=response_body,
            response_time_ms=response_time_ms,
            error=error,
        )
        self.db_session.add(log)
        await self.db_session.flush()
        await self.db_session.refresh(log)
        return log
    
    async def get_logs(
        self,
        webhook_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookLog], int]:
        """Get logs for a specific webhook."""
        query = (
            select(WebhookLog)
            .where(WebhookLog.webhook_id == webhook_id)
            .order_by(desc(WebhookLog.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        count_query = (
            select(func.count())
            .select_from(WebhookLog)
            .where(WebhookLog.webhook_id == webhook_id)
        )
        
        result = await self.db_session.execute(query)
        logs = list(result.scalars().all())
        
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar()
        
        return logs, total

