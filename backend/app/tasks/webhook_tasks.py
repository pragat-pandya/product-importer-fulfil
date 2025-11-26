"""
Webhook-related Celery Tasks
Handles async webhook triggering for product lifecycle events
"""
import asyncio
from typing import Dict, Any
from celery import Task
from celery.utils.log import get_task_logger

from app.core.celery_app import celery_app
from app.db.session import async_session_maker
from app.services.webhook_service import WebhookService

logger = get_task_logger(__name__)


class WebhookTask(Task):
    """Base task class for webhook operations."""
    name = "app.tasks.webhook_tasks.trigger_webhooks"


@celery_app.task(
    bind=True,
    base=WebhookTask,
    name="app.tasks.webhook_tasks.trigger_webhooks_for_event",
    max_retries=2,
    default_retry_delay=30,
)
def trigger_webhooks_for_event(
    self,
    event: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Trigger all active webhooks for a specific event.
    
    This task runs asynchronously to avoid blocking the main request.
    
    Args:
        event: Event type (e.g., "product.created")
        payload: Event data to send to webhooks
        
    Returns:
        Dict with execution results
    """
    logger.info(f"Triggering webhooks for event: {event}")
    
    try:
        # Run async function in event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    async def trigger_all_webhooks():
        """Async function to trigger webhooks."""
        async with async_session_maker() as db_session:
            service = WebhookService(db_session)
            triggered_count = await service.trigger_event(event, payload)
            await db_session.commit()
            return triggered_count
    
    try:
        triggered_count = loop.run_until_complete(trigger_all_webhooks())
        
        logger.info(f"Successfully triggered {triggered_count} webhooks for event: {event}")
        
        return {
            "status": "success",
            "event": event,
            "webhooks_triggered": triggered_count,
            "task_id": self.request.id,
        }
        
    except Exception as exc:
        logger.error(f"Error triggering webhooks for event {event}: {exc}", exc_info=True)
        
        # Retry the task if not at max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            "status": "failed",
            "event": event,
            "error": str(exc),
            "task_id": self.request.id,
        }


@celery_app.task(
    bind=True,
    name="app.tasks.webhook_tasks.trigger_single_webhook",
    max_retries=3,
    default_retry_delay=60,
)
def trigger_single_webhook(
    self,
    webhook_id: str,
    event: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Trigger a specific webhook.
    
    Used for manual webhook execution or retry logic.
    
    Args:
        webhook_id: UUID of webhook to trigger
        event: Event type
        payload: Event data
        
    Returns:
        Dict with execution result
    """
    logger.info(f"Triggering webhook {webhook_id} for event: {event}")
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    async def trigger_webhook():
        """Async function to trigger single webhook."""
        from uuid import UUID
        
        async with async_session_maker() as db_session:
            service = WebhookService(db_session)
            log = await service.execute_webhook(UUID(webhook_id), event, payload)
            await db_session.commit()
            return {
                "success": log.error is None,
                "status_code": log.status_code,
                "response_time_ms": log.response_time_ms,
                "error": log.error,
            }
    
    try:
        result = loop.run_until_complete(trigger_webhook())
        
        logger.info(f"Webhook {webhook_id} triggered successfully")
        
        return {
            "status": "success",
            "webhook_id": webhook_id,
            "event": event,
            "task_id": self.request.id,
            **result,
        }
        
    except Exception as exc:
        logger.error(f"Error triggering webhook {webhook_id}: {exc}", exc_info=True)
        
        # Retry the task if not at max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            "status": "failed",
            "webhook_id": webhook_id,
            "event": event,
            "error": str(exc),
            "task_id": self.request.id,
        }

