"""
Product API Routes
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis

from config import settings
from app.tasks.product_tasks import process_csv_upload


router = APIRouter(prefix="/products", tags=["Products"])

# Create temp directory for uploads
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class UploadResponse(BaseModel):
    """Response model for file upload."""
    task_id: str
    status: str
    message: str
    filename: str


class ImportProgressResponse(BaseModel):
    """Response model for import progress."""
    task_id: str
    status: str
    current: int
    total: int
    created: Optional[int] = None
    updated: Optional[int] = None
    errors: Optional[int] = None
    percent: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    task_id: str
    state: str  # Pending, Processing, Completed, Failed
    progress_percent: Optional[int] = None
    current: Optional[int] = None
    total: Optional[int] = None
    created: Optional[int] = None
    updated: Optional[int] = None
    errors: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(..., description="CSV file to upload"),
) -> UploadResponse:
    """
    Upload a CSV file for product import.
    
    The file is saved to a temporary directory and a Celery task is triggered
    to process it asynchronously.
    
    Args:
        file: CSV file containing product data
        
    Returns:
        Task ID and upload status
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files are allowed."
        )
    
    # Validate file size (max 100MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        safe_filename = f"{timestamp}_{unique_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger Celery task
        task = process_csv_upload.apply_async(
            args=[str(file_path)],
            kwargs={"user_id": None, "options": None}
        )
        
        return UploadResponse(
            task_id=task.id,
            status="submitted",
            message="File uploaded successfully. Processing started.",
            filename=file.filename
        )
        
    except Exception as e:
        # Clean up file if task submission failed
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process upload: {str(e)}"
        )
    finally:
        await file.close()


@router.get("/import/{task_id}/progress", response_model=ImportProgressResponse)
async def get_import_progress(task_id: str) -> ImportProgressResponse:
    """
    Get the progress of a CSV import task.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Current progress information
    """
    try:
        # Try to get progress from Redis first (most up-to-date)
        redis_client = redis.from_url(str(settings.REDIS_URL))
        progress_key = f"celery-task-progress:{task_id}"
        progress_data = redis_client.get(progress_key)
        
        if progress_data:
            import json
            data = json.loads(progress_data)
            return ImportProgressResponse(**data)
        
        # Fallback to Celery result backend
        from celery.result import AsyncResult
        task_result = AsyncResult(task_id, app=process_csv_upload.app)
        
        if task_result.state == 'PENDING':
            return ImportProgressResponse(
                task_id=task_id,
                status='PENDING',
                current=0,
                total=0,
                message='Task is pending...'
            )
        elif task_result.state == 'PROGRESS':
            meta = task_result.info or {}
            return ImportProgressResponse(
                task_id=task_id,
                status='PROGRESS',
                current=meta.get('current', 0),
                total=meta.get('total', 0),
                created=meta.get('created'),
                updated=meta.get('updated'),
                errors=meta.get('errors'),
                percent=meta.get('percent'),
                message=meta.get('message', 'Processing...')
            )
        elif task_result.state == 'SUCCESS':
            result = task_result.result or {}
            return ImportProgressResponse(
                task_id=task_id,
                status='SUCCESS',
                current=result.get('processed_rows', 0),
                total=result.get('total_rows', 0),
                created=result.get('created', 0),
                updated=result.get('updated', 0),
                errors=result.get('errors', 0),
                percent=100,
                message=result.get('message', 'Import completed')
            )
        else:  # FAILURE
            return ImportProgressResponse(
                task_id=task_id,
                status='FAILURE',
                current=0,
                total=0,
                error=str(task_result.info)
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get progress: {str(e)}"
        )


@router.get("/upload/{task_id}/status", response_model=TaskStatusResponse)
async def get_upload_status(task_id: str) -> TaskStatusResponse:
    """
    Get the current status of a CSV upload task.
    
    This endpoint provides a simplified status view with states:
    - Pending: Task is queued but not started
    - Processing: Task is currently running
    - Completed: Task finished successfully
    - Failed: Task encountered an error
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Current task status with progress information
    """
    try:
        # Initialize Redis client
        redis_client = redis.from_url(str(settings.REDIS_URL))
        progress_key = f"celery-task-progress:{task_id}"
        
        # Try to get progress data from Redis (most up-to-date)
        try:
            progress_data = redis_client.get(progress_key)
            
            if progress_data:
                import json
                data = json.loads(progress_data)
                
                # Map Celery status to simplified state
                celery_status = data.get('status', 'PENDING')
                state_mapping = {
                    'PENDING': 'Pending',
                    'PROGRESS': 'Processing',
                    'SUCCESS': 'Completed',
                    'FAILURE': 'Failed',
                    'RETRY': 'Processing',
                }
                state = state_mapping.get(celery_status, celery_status)
                
                return TaskStatusResponse(
                    task_id=task_id,
                    state=state,
                    progress_percent=data.get('percent'),
                    current=data.get('current'),
                    total=data.get('total'),
                    created=data.get('created'),
                    updated=data.get('updated'),
                    errors=data.get('errors'),
                    message=data.get('message'),
                    error=data.get('error')
                )
        except redis.RedisError as e:
            # Redis error - log it but continue to Celery fallback
            print(f"⚠️  Redis error: {e}")
        except json.JSONDecodeError as e:
            # Invalid JSON in Redis - log and continue
            print(f"⚠️  Invalid JSON in Redis: {e}")
        
        # Fallback to Celery result backend
        from celery.result import AsyncResult
        
        try:
            task_result = AsyncResult(task_id, app=process_csv_upload.app)
            
            # Map Celery states to simplified states
            if task_result.state == 'PENDING':
                return TaskStatusResponse(
                    task_id=task_id,
                    state='Pending',
                    progress_percent=0,
                    current=0,
                    total=0,
                    message='Task is queued and waiting to start'
                )
            
            elif task_result.state == 'STARTED' or task_result.state == 'RETRY':
                return TaskStatusResponse(
                    task_id=task_id,
                    state='Processing',
                    progress_percent=0,
                    current=0,
                    total=0,
                    message='Task has started processing'
                )
            
            elif task_result.state == 'PROGRESS':
                meta = task_result.info or {}
                return TaskStatusResponse(
                    task_id=task_id,
                    state='Processing',
                    progress_percent=meta.get('percent', 0),
                    current=meta.get('current', 0),
                    total=meta.get('total', 0),
                    created=meta.get('created'),
                    updated=meta.get('updated'),
                    errors=meta.get('errors'),
                    message=meta.get('message', 'Processing CSV file...')
                )
            
            elif task_result.state == 'SUCCESS':
                result = task_result.result or {}
                return TaskStatusResponse(
                    task_id=task_id,
                    state='Completed',
                    progress_percent=100,
                    current=result.get('processed_rows', 0),
                    total=result.get('total_rows', 0),
                    created=result.get('created', 0),
                    updated=result.get('updated', 0),
                    errors=result.get('errors', 0),
                    message='Import completed successfully'
                )
            
            elif task_result.state == 'FAILURE':
                error_info = str(task_result.info) if task_result.info else 'Unknown error'
                return TaskStatusResponse(
                    task_id=task_id,
                    state='Failed',
                    progress_percent=0,
                    current=0,
                    total=0,
                    error=error_info,
                    message='Import failed'
                )
            
            else:
                # Unknown state - return as-is
                return TaskStatusResponse(
                    task_id=task_id,
                    state=task_result.state,
                    progress_percent=0,
                    current=0,
                    total=0,
                    message=f'Task in {task_result.state} state'
                )
                
        except Exception as celery_error:
            # Celery error - log and return error response
            print(f"❌ Celery error: {celery_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve task status from Celery: {str(celery_error)}"
            )
            
    except redis.ConnectionError as e:
        # Redis connection failed entirely
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(e)}. Progress tracking unavailable."
        )
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"❌ Unexpected error in get_upload_status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/import/{task_id}/result")
async def get_import_result(task_id: str) -> Dict[str, Any]:
    """
    Get the final result of a completed import task.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Import results and statistics
    """
    try:
        from celery.result import AsyncResult
        task_result = AsyncResult(task_id, app=process_csv_upload.app)
        
        if not task_result.ready():
            raise HTTPException(
                status_code=400,
                detail="Task is not completed yet. Check progress endpoint."
            )
        
        if task_result.successful():
            return {
                "status": "success",
                "task_id": task_id,
                "result": task_result.result
            }
        else:
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(task_result.info)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get result: {str(e)}"
        )

