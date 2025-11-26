"""
Product API Routes
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4, UUID

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import redis
from celery.result import AsyncResult

from config import settings
from app.tasks.product_tasks import process_csv_upload, bulk_delete_products
from app.db.session import get_db
from app.services.product_service import ProductService
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)


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
    
    # Initialize file_path before try block
    file_path = None
    
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
        if file_path and file_path.exists():
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
        try:
            from app.core.celery_app import celery_app
            task_result = AsyncResult(task_id, app=celery_app)
            
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
        from app.core.celery_app import celery_app
        task_result = AsyncResult(task_id, app=celery_app)
        
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


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.get("", response_model=ProductListResponse, summary="List Products")
async def list_products(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    sku: Optional[str] = Query(default=None, description="Filter by SKU (partial match)"),
    name: Optional[str] = Query(default=None, description="Filter by name (partial match)"),
    active: Optional[bool] = Query(default=None, description="Filter by active status"),
    db_session: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """
    Get a paginated list of products with optional filtering.
    
    Supports:
    - **Pagination**: Use `limit` and `offset` parameters
    - **Filtering**: By SKU, name, or active status
    - **Case-insensitive search**: SKU and name filters are case-insensitive
    
    Args:
        limit: Number of products to return (1-100, default: 20)
        offset: Number of products to skip (default: 0)
        sku: Optional SKU filter (case-insensitive partial match)
        name: Optional name filter (case-insensitive partial match)
        active: Optional active status filter (true/false)
        db_session: Database session (injected)
        
    Returns:
        Paginated list of products with total count
        
    Example:
        GET /products?limit=10&offset=0&active=true&name=widget
    """
    service = ProductService(db_session)
    
    products, total = await service.get_products(
        limit=limit,
        offset=offset,
        sku=sku,
        name=name,
        active=active,
    )
    
    # Convert to response models
    product_responses = [ProductResponse.model_validate(p) for p in products]
    
    return ProductListResponse(
        items=product_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.post("", response_model=ProductResponse, status_code=201, summary="Create Product")
async def create_product(
    product_data: ProductCreate,
    db_session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Create a new product.
    
    The SKU must be unique (case-insensitive). If a product with the same SKU
    already exists, a 409 Conflict error will be returned.
    
    Args:
        product_data: Product data to create
        db_session: Database session (injected)
        
    Returns:
        Created product
        
    Raises:
        HTTPException 409: If SKU already exists
        
    Example:
        POST /products
        {
            "sku": "WIDGET-001",
            "name": "Premium Widget",
            "description": "High-quality widget",
            "active": true
        }
    """
    service = ProductService(db_session)
    product = await service.create_product(product_data)
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get Product by ID")
async def get_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Get a single product by its ID.
    
    Args:
        product_id: Product UUID
        db_session: Database session (injected)
        
    Returns:
        Product details
        
    Raises:
        HTTPException 404: If product not found
        
    Example:
        GET /products/123e4567-e89b-12d3-a456-426614174000
    """
    service = ProductService(db_session)
    product = await service.get_product_by_id(product_id)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse, summary="Update Product")
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db_session: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Update an existing product.
    
    Only the fields provided in the request body will be updated.
    Other fields will remain unchanged.
    
    If updating the SKU, the new SKU must be unique (case-insensitive).
    
    Args:
        product_id: Product UUID to update
        product_data: Product data to update (partial update supported)
        db_session: Database session (injected)
        
    Returns:
        Updated product
        
    Raises:
        HTTPException 404: If product not found
        HTTPException 409: If new SKU already exists
        
    Example:
        PUT /products/123e4567-e89b-12d3-a456-426614174000
        {
            "name": "Updated Widget Name",
            "active": false
        }
    """
    service = ProductService(db_session)
    product = await service.update_product(product_id, product_data)
    return ProductResponse.model_validate(product)


class BulkDeleteResponse(BaseModel):
    """Response model for bulk delete operation."""
    task_id: str
    status: str
    message: str


@router.delete("/all", response_model=BulkDeleteResponse, summary="Bulk Delete All Products")
async def delete_all_products() -> BulkDeleteResponse:
    """
    Delete all products in the database as a background task.
    
    This operation is performed asynchronously via a Celery task to avoid
    blocking the API for large datasets. Use the task ID to monitor progress.
    
    ⚠️ **WARNING**: This operation cannot be undone!
    
    Returns:
        Task ID and status for monitoring the deletion progress
        
    Example:
        DELETE /products/all
        
    Response:
        {
            "task_id": "abc123...",
            "status": "submitted",
            "message": "Bulk delete task submitted. Use task ID to monitor progress."
        }
        
    To check progress:
        GET /products/delete/{task_id}/status
    """
    # Trigger Celery task for bulk delete
    task = bulk_delete_products.apply_async()
    
    return BulkDeleteResponse(
        task_id=task.id,
        status="submitted",
        message="Bulk delete task submitted. Use task ID to monitor progress.",
    )


@router.delete("/{product_id}", status_code=204, summary="Delete Product")
async def delete_product(
    product_id: UUID,
    db_session: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a single product by its ID.
    
    Args:
        product_id: Product UUID to delete
        db_session: Database session (injected)
        
    Returns:
        No content (204 status)
        
    Raises:
        HTTPException 404: If product not found
        
    Example:
        DELETE /products/123e4567-e89b-12d3-a456-426614174000
    """
    service = ProductService(db_session)
    await service.delete_product(product_id)


@router.get("/delete/{task_id}/status", summary="Get Bulk Delete Task Status")
async def get_bulk_delete_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a bulk delete task.
    
    Args:
        task_id: The Celery task ID from the bulk delete operation
        
    Returns:
        Current task status with progress information
        
    Example:
        GET /products/delete/{task_id}/status
    """
    try:
        # Initialize Redis client
        redis_client = redis.from_url(str(settings.REDIS_URL))
        progress_key = f"celery-task-progress:{task_id}"
        
        # Try to get progress data from Redis
        try:
            progress_data = redis_client.get(progress_key)
            
            if progress_data:
                data = json.loads(progress_data)
                return {
                    "task_id": task_id,
                    "status": data.get('status', 'PENDING'),
                    "message": data.get('message', 'Processing...'),
                    "percent": data.get('percent', 0),
                    "deleted_count": data.get('deleted_count'),
                    "error": data.get('error'),
                }
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"⚠️  Redis error: {e}")
        
        # Fallback to Celery result backend
        from app.core.celery_app import celery_app
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == 'PENDING':
            return {
                "task_id": task_id,
                "status": "PENDING",
                "message": "Task is queued and waiting to start",
                "percent": 0,
            }
        elif task_result.state == 'PROGRESS':
            meta = task_result.info or {}
            return {
                "task_id": task_id,
                "status": "PROGRESS",
                "message": meta.get('message', 'Deleting products...'),
                "percent": meta.get('percent', 0),
            }
        elif task_result.state == 'SUCCESS':
            result = task_result.result or {}
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "message": result.get('message', 'Bulk delete completed'),
                "percent": 100,
                "deleted_count": result.get('deleted_count', 0),
            }
        elif task_result.state == 'FAILURE':
            error_info = str(task_result.info) if task_result.info else 'Unknown error'
            return {
                "task_id": task_id,
                "status": "FAILURE",
                "message": "Bulk delete failed",
                "error": error_info,
                "percent": 0,
            }
        else:
            return {
                "task_id": task_id,
                "status": task_result.state,
                "message": f"Task in {task_result.state} state",
                "percent": 0,
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

