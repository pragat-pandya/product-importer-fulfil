"""
Celery Worker Configuration
"""
from celery import Celery
from config import settings

# Initialize Celery app
celery_app = Celery(
    "fulfil_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["celery_app.tasks"])


@celery_app.task(bind=True, name="celery_app.test_task")
def test_task(self):
    """
    Test task to verify Celery is working correctly.
    """
    return {
        "status": "success",
        "message": "Celery worker is running! 🎉",
        "task_id": self.request.id,
    }

