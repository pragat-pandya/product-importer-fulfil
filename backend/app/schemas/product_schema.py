"""
Product Pydantic Schemas for Request/Response Validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Base Product schema with common fields."""
    
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    active: bool = Field(default=True, description="Product active status")


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sku": "PROD-001",
                "name": "Premium Widget",
                "description": "High-quality widget for professionals",
                "active": True,
            }
        }
    )


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    
    sku: Optional[str] = Field(None, min_length=1, max_length=100, description="Stock Keeping Unit")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    active: Optional[bool] = Field(None, description="Product active status")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Product Name",
                "description": "Updated description",
                "active": False,
            }
        }
    )


class ProductResponse(ProductBase):
    """Schema for product response."""
    
    id: UUID = Field(..., description="Product unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "sku": "PROD-001",
                "name": "Premium Widget",
                "description": "High-quality widget",
                "active": True,
                "created_at": "2025-11-26T15:00:00Z",
                "updated_at": "2025-11-26T15:00:00Z",
            }
        }
    )


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    
    items: List[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products matching filters")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether there are more items")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "sku": "PROD-001",
                        "name": "Premium Widget",
                        "description": "High-quality widget",
                        "active": True,
                        "created_at": "2025-11-26T15:00:00Z",
                        "updated_at": "2025-11-26T15:00:00Z",
                    }
                ],
                "total": 100,
                "limit": 20,
                "offset": 0,
                "has_more": True,
            }
        }
    )

