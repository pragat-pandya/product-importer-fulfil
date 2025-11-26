"""
Celery Task Management API Routes
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.celery_app import celery_app
from app.tasks.product_tasks import test_task


router = APIRouter(prefix="/celery", tags=["Celery"])


class TaskResponse(BaseModel):
    """Response model for task submission."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status check."""
    task_id: str
    status: str
    result: Dict[str, Any] | None = None
    error: str | None = None


@router.get("/workers", response_model=Dict[str, Any])
async def get_workers():
    """
    Get information about active Celery workers.
    
    Returns:
        Dict containing active workers and their status
    """
    try:
        # Get active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        stats = inspect.stats()
        registered_tasks = inspect.registered()
        
        return {
            "status": "success",
            "workers": {
                "active": active_workers or {},
                "stats": stats or {},
                "registered_tasks": registered_tasks or {},
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get worker info: {str(e)}")


@router.post("/test", response_model=TaskResponse)
async def trigger_test_task():
    """
    Trigger a test task to verify Celery is working.
    
    Returns:
        Task ID and status
    """
    try:
        result = test_task.apply_async()
        return TaskResponse(
            task_id=result.id,
            status="submitted",
            message="Test task has been submitted to the worker"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a Celery task by ID.
    
    Args:
        task_id: The Celery task ID
        
    Returns:
        Task status and result if completed
    """
    try:
        from celery.result import AsyncResult
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_result.status,
        )
        
        if task_result.ready():
            if task_result.successful():
                response.result = task_result.result
            else:
                response.error = str(task_result.result)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.delete("/task/{task_id}")
async def revoke_task(task_id: str):
    """
    Revoke (cancel) a running task.
    
    Args:
        task_id: The Celery task ID to revoke
        
    Returns:
        Confirmation message
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "status": "success",
            "message": f"Task {task_id} has been revoked",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke task: {str(e)}")

