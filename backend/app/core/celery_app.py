"""
Celery Application Configuration
"""
from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from config import settings


def create_celery_app() -> Celery:
    """
    Create and configure Celery application.
    
    Returns:
        Celery: Configured Celery application instance
    """
    celery_app = Celery(
        "fulfil_worker",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=[
            "app.tasks.product_tasks",
            "app.tasks.webhook_tasks",
            # Add more task modules here as needed
        ]
    )
    
    # Configure Celery
    celery_app.conf.update(
        # Serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        
        # Timezone
        timezone="UTC",
        enable_utc=True,
        
        # Task execution
        task_track_started=True,
        task_time_limit=3600,  # 1 hour hard limit
        task_soft_time_limit=3300,  # 55 minutes soft limit
        task_acks_late=True,  # Acknowledge tasks after completion
        task_reject_on_worker_lost=True,  # Re-queue tasks if worker dies
        
        # Worker
        worker_prefetch_multiplier=1,  # One task at a time for long-running tasks
        worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
        worker_disable_rate_limits=False,
        
        # Results
        result_expires=3600,  # Results expire after 1 hour
        result_persistent=True,  # Persist results
        
        # Broker settings
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        
        # Task routes (optional - for future queue management)
        # task_routes={
        #     "app.tasks.product_tasks.process_csv_import": {"queue": "csv_import"},
        #     "app.tasks.product_tasks.*": {"queue": "default"},
        # },
        
        # Beat schedule (for future scheduled tasks)
        beat_schedule={},
    )
    
    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """
    Signal handler when worker is ready.
    """
    pass


@worker_shutdown.connect
def on_worker_shutdown(sender, **kwargs):
    """
    Signal handler when worker is shutting down.
    """
    pass


# Expose for imports
__all__ = ["celery_app", "create_celery_app"]

