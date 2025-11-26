"""
Product-related Celery Tasks
"""
import json
from typing import Any, Dict
from pathlib import Path
from celery import Task
import redis

from app.core.celery_app import celery_app
from app.services.import_service import ImportService
from config import settings


class DatabaseTask(Task):
    """
    Base task class that provides database session handling.
    """
    _db_session = None
    
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Clean up database session after task completes.
        """
        if self._db_session is not None:
            self._db_session.close()
            self._db_session = None


@celery_app.task(
    bind=True,
    name="app.tasks.product_tasks.test_task",
    max_retries=3,
    default_retry_delay=60,
)
def test_task(self) -> Dict[str, Any]:
    """
    Test task to verify Celery is working correctly.
    
    Returns:
        Dict with status and task information
    """
    return {
        "status": "success",
        "message": "Celery worker is functioning correctly! 🎉",
        "task_id": self.request.id,
        "task_name": self.name,
    }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.product_tasks.process_csv_upload",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    time_limit=3600,  # 1 hour
    soft_time_limit=3300,  # 55 minutes
)
def process_csv_upload(
    self,
    file_path: str,
    user_id: str | None = None,
    options: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Process CSV file upload and import products.
    
    Features:
    - Chunked CSV reading for memory efficiency
    - Case-insensitive SKU upsert logic
    - Progress tracking in Redis
    - Detailed error reporting
    
    Args:
        file_path: Path to the CSV file to process
        user_id: Optional user ID who initiated the import
        options: Optional processing options
        
    Returns:
        Dict with processing results
    """
    # Initialize Redis for progress tracking
    redis_client = redis.from_url(str(settings.REDIS_URL))
    task_id = self.request.id
    progress_key = f"celery-task-progress:{task_id}"
    
    def update_progress(stats: Dict[str, Any]):
        """Update progress in Redis and Celery state."""
        progress_data = {
            "task_id": task_id,
            "status": "PROGRESS",
            "current": stats['processed_rows'],
            "total": stats['total_rows'],
            "created": stats['created'],
            "updated": stats['updated'],
            "errors": stats['errors'],
            "percent": int((stats['processed_rows'] / stats['total_rows'] * 100)) if stats['total_rows'] > 0 else 0,
        }
        
        # Store in Redis (expires in 1 hour)
        redis_client.setex(
            progress_key,
            3600,
            json.dumps(progress_data)
        )
        
        # Update Celery state
        self.update_state(
            state="PROGRESS",
            meta=progress_data
        )
    
    try:
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Initialize progress
        self.update_state(
            state="PROGRESS",
            meta={
                "task_id": task_id,
                "status": "PROGRESS",
                "current": 0,
                "total": 0,
                "message": "Starting CSV import...",
            }
        )
        
        # Create import service and process file
        import_service = ImportService()
        
        # Use asyncio to run the async function
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            import_service.process_csv_file(
                file_path=file_path,
                progress_callback=update_progress
            )
        )
        
        # Final progress update
        final_progress = {
            "task_id": task_id,
            "status": "SUCCESS",
            "current": result['processed_rows'],
            "total": result['total_rows'],
            "created": result['created'],
            "updated": result['updated'],
            "errors": result['errors'],
            "percent": 100,
        }
        redis_client.setex(progress_key, 3600, json.dumps(final_progress))
        
        # Clean up file after successful processing
        try:
            Path(file_path).unlink()
        except Exception:
            pass
        
        return {
            "status": "success",
            "message": "CSV import completed successfully",
            "task_id": task_id,
            "file_path": file_path,
            "user_id": user_id,
            **result
        }
        
    except Exception as exc:
        # Get error message
        error_msg = str(exc)
        
        # Update Redis with error
        error_data = {
            "task_id": task_id,
            "status": "FAILURE",
            "error": error_msg,
        }
        redis_client.setex(progress_key, 3600, json.dumps(error_data))
        
        # Retry the task if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            raise


@celery_app.task(
    bind=True,
    name="app.tasks.product_tasks.cleanup_old_imports",
)
def cleanup_old_imports(self) -> Dict[str, Any]:
    """
    Cleanup old import files and data.
    
    This task can be scheduled to run periodically to clean up
    old CSV files and import records.
    
    Returns:
        Dict with cleanup results
    """
    # TODO: Implement cleanup logic
    return {
        "status": "success",
        "message": "Cleanup completed",
        "task_id": self.request.id,
        "files_deleted": 0,
        "records_deleted": 0,
    }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.product_tasks.bulk_delete_products",
    max_retries=2,
    default_retry_delay=60,  # 1 minute
    time_limit=1800,  # 30 minutes
    soft_time_limit=1650,  # 27.5 minutes
)
def bulk_delete_products(self) -> Dict[str, Any]:
    """
    Delete all products in the database as a background task.
    
    This is a long-running task that should be used when deleting
    a large number of products to avoid blocking the API.
    
    Features:
    - Progress tracking in Redis
    - Transaction handling for data integrity
    - Error recovery and retry logic
    
    Returns:
        Dict with deletion results
    """
    # Initialize Redis for progress tracking
    redis_client = redis.from_url(str(settings.REDIS_URL))
    task_id = self.request.id
    progress_key = f"celery-task-progress:{task_id}"
    
    try:
        # Initialize progress
        self.update_state(
            state="PROGRESS",
            meta={
                "task_id": task_id,
                "status": "PROGRESS",
                "message": "Initializing bulk delete...",
                "percent": 0,
            }
        )
        
        redis_client.setex(
            progress_key,
            3600,
            json.dumps({
                "task_id": task_id,
                "status": "PROGRESS",
                "message": "Counting products...",
                "percent": 10,
            })
        )
        
        # Use asyncio to run the async database operations
        import asyncio
        from app.db.session import async_session_maker
        from app.services.product_service import ProductService
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        async def perform_bulk_delete():
            """Async function to perform the bulk delete."""
            async with async_session_maker() as db_session:
                service = ProductService(db_session)
                
                # Count products first
                total_count = await service.count_all_products()
                
                # Update progress
                redis_client.setex(
                    progress_key,
                    3600,
                    json.dumps({
                        "task_id": task_id,
                        "status": "PROGRESS",
                        "message": f"Deleting {total_count} products...",
                        "percent": 30,
                        "total_count": total_count,
                    })
                )
                
                # Perform bulk delete
                deleted_count = await service.delete_all_products()
                
                # Commit the transaction
                await db_session.commit()
                
                return {
                    "total_count": total_count,
                    "deleted_count": deleted_count,
                }
        
        result = loop.run_until_complete(perform_bulk_delete())
        
        # Final progress update
        final_progress = {
            "task_id": task_id,
            "status": "SUCCESS",
            "message": f"Successfully deleted {result['deleted_count']} products",
            "percent": 100,
            "deleted_count": result['deleted_count'],
        }
        redis_client.setex(progress_key, 3600, json.dumps(final_progress))
        
        return {
            "status": "success",
            "message": f"Successfully deleted {result['deleted_count']} products",
            "task_id": task_id,
            "deleted_count": result['deleted_count'],
        }
        
    except Exception as exc:
        # Get error message
        error_msg = str(exc)
        
        # Update Redis with error
        error_data = {
            "task_id": task_id,
            "status": "FAILURE",
            "error": error_msg,
            "message": "Bulk delete failed",
        }
        redis_client.setex(progress_key, 3600, json.dumps(error_data))
        
        # Retry the task if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        else:
            raise
    finally:
        redis_client.close()

