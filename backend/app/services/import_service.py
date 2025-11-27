"""
Import Service for CSV Processing

Handles CSV file reading, validation, and product upsert operations.
"""
import csv
from pathlib import Path
from typing import Dict, Any, List, Generator, Optional, Callable
from datetime import datetime
import pandas as pd
from sqlalchemy import insert, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.db.session import async_session_maker


class ImportService:
    """
    Service for handling product CSV imports.
    
    Features:
    - Chunked CSV reading for memory efficiency
    - Case-insensitive SKU duplicate detection
    - Upsert operations (insert or update)
    - Validation and error tracking
    """
    
    CHUNK_SIZE = 1000  # Process 1000 rows at a time
    REQUIRED_COLUMNS = {'sku', 'name'}  # Minimum required columns
    OPTIONAL_COLUMNS = {'description', 'active'}
    
    def __init__(self):
        """Initialize the import service."""
        self.errors: List[Dict[str, Any]] = []
        self.stats = {
            "total_rows": 0,
            "processed_rows": 0,
            "created": 0,
            "updated": 0,
            "errors": 0,
            "skipped": 0,
        }
    
    @staticmethod
    def read_csv_chunks(file_path: str, chunk_size: int = 1000) -> Generator[pd.DataFrame, None, None]:
        """
        Read CSV file in chunks for memory efficiency.
        
        Args:
            file_path: Path to the CSV file
            chunk_size: Number of rows per chunk
            
        Yields:
            DataFrame chunks
        """
        try:
            # Try pandas C engine first (faster for large files)
            # Use on_bad_lines='skip' to handle rows with incorrect number of fields
            # This can happen when fields contain unquoted commas
            try:
                for chunk in pd.read_csv(
                    file_path,
                    chunksize=chunk_size,
                    encoding='utf-8',
                    dtype=str,  # Read all as strings initially
                    na_values=['', 'NULL', 'null', 'None'],
                    keep_default_na=True,
                    on_bad_lines='skip',  # Skip malformed lines instead of raising error
                    quotechar='"',  # Standard CSV quote character
                    skipinitialspace=True,
                ):
                    yield chunk
            except Exception as e:
                # Catch parsing errors - could be ParserError, CParserError, or ValueError
                # Different pandas versions use different exception types
                # If C engine fails, try Python engine which is more forgiving
                # Python engine can handle inconsistent field counts better
                # Only retry if it's likely a parsing error, not other exceptions
                error_str = str(e).lower()
                if 'parser' not in error_str and 'field' not in error_str and 'tokenizing' not in error_str:
                    # Not a parsing error, re-raise
                    raise
                for chunk in pd.read_csv(
                    file_path,
                    chunksize=chunk_size,
                    encoding='utf-8',
                    dtype=str,
                    na_values=['', 'NULL', 'null', 'None'],
                    keep_default_na=True,
                    on_bad_lines='skip',
                    quotechar='"',
                    skipinitialspace=True,
                    engine='python',  # More forgiving engine
                ):
                    yield chunk
        except Exception as e:
            # Fallback to standard csv module
            raise ValueError(f"Failed to read CSV file: {str(e)}")
    
    @staticmethod
    def validate_csv_structure(file_path: str) -> tuple[bool, str, List[str]]:
        """
        Validate CSV file structure before processing.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple of (is_valid, error_message, columns)
        """
        try:
            # Read first chunk to check structure
            # Use same parameters as read_csv_chunks for consistency
            try:
                df = pd.read_csv(
                    file_path,
                    nrows=1,
                    encoding='utf-8',
                    on_bad_lines='skip',
                    quotechar='"',
                    skipinitialspace=True,
                )
            except Exception:
                # Catch parsing errors - could be ParserError, CParserError, or ValueError
                # Different pandas versions use different exception types
                # Fallback to Python engine if C engine fails
                df = pd.read_csv(
                    file_path,
                    nrows=1,
                    encoding='utf-8',
                    on_bad_lines='skip',
                    quotechar='"',
                    skipinitialspace=True,
                    engine='python',
                )
            columns = [col.strip().lower() for col in df.columns]
            
            # Check for required columns
            missing_columns = ImportService.REQUIRED_COLUMNS - set(columns)
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", columns
            
            return True, "", columns
            
        except Exception as e:
            return False, f"Failed to validate CSV: {str(e)}", []
    
    def validate_row(self, row: Dict[str, Any], row_number: int) -> tuple[bool, Optional[str]]:
        """
        Validate a single row of data.
        
        Args:
            row: Dictionary of column values
            row_number: Row number for error reporting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check SKU
        if not row.get('sku') or pd.isna(row.get('sku')):
            return False, f"Row {row_number}: SKU is required"
        
        sku = str(row['sku']).strip()
        if len(sku) > 100:
            return False, f"Row {row_number}: SKU exceeds 100 characters"
        
        # Check name
        if not row.get('name') or pd.isna(row.get('name')):
            return False, f"Row {row_number}: Name is required"
        
        name = str(row['name']).strip()
        if len(name) > 255:
            return False, f"Row {row_number}: Name exceeds 255 characters"
        
        return True, None
    
    def normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and clean row data.
        
        Args:
            row: Raw row data
            
        Returns:
            Normalized row data
        """
        normalized = {}
        
        # SKU - required, trimmed
        normalized['sku'] = str(row.get('sku', '')).strip()
        
        # Name - required, trimmed
        normalized['name'] = str(row.get('name', '')).strip()
        
        # Description - optional, trimmed
        description = row.get('description')
        if description and not pd.isna(description):
            normalized['description'] = str(description).strip()
        else:
            normalized['description'] = None
        
        # Active - optional, boolean
        active = row.get('active', True)
        if pd.isna(active):
            normalized['active'] = True
        elif isinstance(active, str):
            normalized['active'] = active.lower() in ('true', '1', 'yes', 'active')
        else:
            normalized['active'] = bool(active)
        
        return normalized
    
    async def upsert_products_batch(
        self,
        session: AsyncSession,
        products: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Upsert a batch of products using PostgreSQL's ON CONFLICT.
        
        Args:
            session: Database session
            products: List of product dictionaries
            
        Returns:
            Tuple of (created_count, updated_count)
        """
        if not products:
            return 0, 0
        
        # First, check which SKUs already exist (case-insensitive)
        skus = [p['sku'] for p in products]
        existing_query = select(Product.sku).where(
            func.lower(Product.sku).in_([s.lower() for s in skus])
        )
        result = await session.execute(existing_query)
        existing_skus = {row[0].lower() for row in result}
        
        created = 0
        updated = 0
        
        # Use PostgreSQL's INSERT ... ON CONFLICT DO UPDATE
        for product in products:
            sku_lower = product['sku'].lower()
            
            # Prepare insert statement
            stmt = pg_insert(Product).values(
                sku=product['sku'],
                name=product['name'],
                description=product.get('description'),
                active=product.get('active', True),
            )
            
            # Add ON CONFLICT clause for case-insensitive SKU matching
            stmt = stmt.on_conflict_do_update(
                index_elements=[func.lower(Product.sku)],
                set_={
                    'name': stmt.excluded.name,
                    'description': stmt.excluded.description,
                    'active': stmt.excluded.active,
                    'updated_at': func.now(),
                }
            )
            
            await session.execute(stmt)
            
            # Track whether it was an insert or update
            if sku_lower in existing_skus:
                updated += 1
            else:
                created += 1
        
        await session.commit()
        return created, updated
    
    async def process_csv_file(
        self,
        file_path: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process a CSV file and import products.
        
        Args:
            file_path: Path to the CSV file
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with import statistics
        """
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate CSV structure
        is_valid, error_msg, columns = self.validate_csv_structure(file_path)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Count total rows for progress tracking
        try:
            self.stats['total_rows'] = sum(1 for _ in open(file_path)) - 1  # Exclude header
        except Exception:
            self.stats['total_rows'] = 0
        
        # Process file in chunks
        batch = []
        row_number = 1  # Start from 1 (header is 0)
        
        for chunk in self.read_csv_chunks(file_path, self.CHUNK_SIZE):
            # Normalize column names
            chunk.columns = [col.strip().lower() for col in chunk.columns]
            
            for _, row in chunk.iterrows():
                row_number += 1
                
                # Validate row
                is_valid, error_msg = self.validate_row(row.to_dict(), row_number)
                if not is_valid:
                    self.errors.append({
                        "row": row_number,
                        "error": error_msg,
                        "data": row.to_dict(),
                    })
                    self.stats['errors'] += 1
                    continue
                
                # Normalize and add to batch
                normalized = self.normalize_row(row.to_dict())
                batch.append(normalized)
                
                # Process batch when it reaches chunk size
                if len(batch) >= self.CHUNK_SIZE:
                    async with async_session_maker() as session:
                        created, updated = await self.upsert_products_batch(session, batch)
                        self.stats['created'] += created
                        self.stats['updated'] += updated
                        self.stats['processed_rows'] += len(batch)
                    
                    # Call progress callback
                    if progress_callback:
                        progress_callback(self.stats)
                    
                    batch = []
            
            # Small delay to prevent overwhelming the database
            # await asyncio.sleep(0.01)
        
        # Process remaining batch
        if batch:
            async with async_session_maker() as session:
                created, updated = await self.upsert_products_batch(session, batch)
                self.stats['created'] += created
                self.stats['updated'] += updated
                self.stats['processed_rows'] += len(batch)
            
            if progress_callback:
                progress_callback(self.stats)
        
        return {
            "status": "completed",
            "total_rows": self.stats['total_rows'],
            "processed_rows": self.stats['processed_rows'],
            "created": self.stats['created'],
            "updated": self.stats['updated'],
            "errors": self.stats['errors'],
            "skipped": self.stats['skipped'],
            "error_details": self.errors[:100],  # Limit to first 100 errors
        }

