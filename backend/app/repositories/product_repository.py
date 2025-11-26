"""
Product Repository - Data Access Layer
Handles all database operations for Product model.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate


class ProductRepository:
    """Repository for Product CRUD operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID."""
        result = await self.db_session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU (case-insensitive)."""
        result = await self.db_session.execute(
            select(Product).where(func.lower(Product.sku) == sku.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_all(
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
        # Build query with filters
        query = select(Product)
        count_query = select(func.count()).select_from(Product)
        
        # Apply filters
        if sku:
            query = query.where(func.lower(Product.sku).contains(sku.lower()))
            count_query = count_query.where(func.lower(Product.sku).contains(sku.lower()))
        
        if name:
            query = query.where(func.lower(Product.name).contains(name.lower()))
            count_query = count_query.where(func.lower(Product.name).contains(name.lower()))
        
        if active is not None:
            query = query.where(Product.active == active)
            count_query = count_query.where(Product.active == active)
        
        # Apply ordering and pagination
        query = query.order_by(Product.created_at.desc()).limit(limit).offset(offset)
        
        # Execute queries
        result = await self.db_session.execute(query)
        products = list(result.scalars().all())
        
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar()
        
        return products, total
    
    async def create(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(
            sku=product_data.sku,
            name=product_data.name,
            description=product_data.description,
            active=product_data.active,
        )
        self.db_session.add(product)
        await self.db_session.flush()  # Flush to get the ID without committing
        await self.db_session.refresh(product)  # Refresh to get generated fields
        return product
    
    async def update(self, product: Product, product_data: ProductUpdate) -> Product:
        """Update an existing product."""
        update_data = product_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await self.db_session.flush()
        await self.db_session.refresh(product)
        return product
    
    async def delete(self, product: Product) -> None:
        """Delete a product."""
        await self.db_session.delete(product)
        await self.db_session.flush()
    
    async def delete_all(self) -> int:
        """
        Delete all products.
        
        Returns:
            Number of deleted products
        """
        result = await self.db_session.execute(delete(Product))
        await self.db_session.flush()
        return result.rowcount
    
    async def count_all(self) -> int:
        """Count all products in the database."""
        result = await self.db_session.execute(select(func.count()).select_from(Product))
        return result.scalar()

