"""
Product Service - Business Logic Layer
Handles business logic for Product operations.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.models.product import Product


class ProductService:
    """Service for Product business logic."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = ProductRepository(db_session)
    
    async def get_product_by_id(self, product_id: UUID) -> Product:
        """
        Get a product by ID.
        
        Raises:
            HTTPException: If product not found.
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        return product
    
    async def get_products(
        self,
        limit: int = 20,
        offset: int = 0,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Tuple[List[Product], int]:
        """
        Get all products with pagination and optional filtering.
        
        Returns:
            Tuple of (products_list, total_count)
        """
        products, total = await self.repository.get_all(
            limit=limit,
            offset=offset,
            sku=sku,
            name=name,
            active=active,
        )
        return products, total
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product.
        
        Raises:
            HTTPException: If SKU already exists.
        """
        # Check if SKU already exists (case-insensitive)
        existing_product = await self.repository.get_by_sku(product_data.sku)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{product_data.sku}' already exists"
            )
        
        product = await self.repository.create(product_data)
        return product
    
    async def update_product(self, product_id: UUID, product_data: ProductUpdate) -> Product:
        """
        Update an existing product.
        
        Raises:
            HTTPException: If product not found or SKU already exists.
        """
        # Get existing product
        product = await self.get_product_by_id(product_id)
        
        # If updating SKU, check if new SKU already exists
        if product_data.sku and product_data.sku.lower() != product.sku.lower():
            existing_product = await self.repository.get_by_sku(product_data.sku)
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Product with SKU '{product_data.sku}' already exists"
                )
        
        updated_product = await self.repository.update(product, product_data)
        return updated_product
    
    async def delete_product(self, product_id: UUID) -> None:
        """
        Delete a product.
        
        Raises:
            HTTPException: If product not found.
        """
        product = await self.get_product_by_id(product_id)
        await self.repository.delete(product)
    
    async def delete_all_products(self) -> int:
        """
        Delete all products.
        
        Returns:
            Number of deleted products.
        """
        deleted_count = await self.repository.delete_all()
        return deleted_count
    
    async def count_all_products(self) -> int:
        """Count all products in the database."""
        return await self.repository.count_all()

