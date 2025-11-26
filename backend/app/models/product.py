"""
Product Model
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    """
    Product model for storing product information.
    
    Attributes:
        id: Unique identifier (UUID)
        sku: Stock Keeping Unit (case-insensitive unique)
        name: Product name
        description: Product description (optional)
        active: Product active status
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last updated
    """
    
    __tablename__ = "products"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        nullable=False,
        doc="Unique identifier"
    )
    
    # SKU - Case-insensitive unique
    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=False,  # Handled by functional index below
        index=True,
        doc="Stock Keeping Unit (case-insensitive unique)"
    )
    
    # Product Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Product name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Product description"
    )
    
    # Status
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Product active status"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when product was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when product was last updated"
    )
    
    # Indexes
    __table_args__ = (
        # Case-insensitive unique index on SKU using LOWER()
        Index(
            "uq_products_sku_lower",
            func.lower(sku),
            unique=True,
            postgresql_ops={"sku": "text_pattern_ops"}
        ),
        # Composite index for active products lookup
        Index("ix_products_active_created", active, created_at.desc()),
    )
    
    def __repr__(self) -> str:
        """String representation of Product."""
        return f"<Product(id={self.id}, sku={self.sku}, name={self.name}, active={self.active})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

