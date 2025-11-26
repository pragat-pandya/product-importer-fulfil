# Product CRUD API Endpoints Documentation

Complete reference for Product CRUD operations in the FulFil Product Importer.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [List Products](#1-list-products)
  - [Get Product by ID](#2-get-product-by-id)
  - [Create Product](#3-create-product)
  - [Update Product](#4-update-product)
  - [Delete Product](#5-delete-product)
  - [Bulk Delete All Products](#6-bulk-delete-all-products)
  - [Get Bulk Delete Status](#7-get-bulk-delete-status)
- [Schemas](#schemas)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

The Product CRUD API provides comprehensive endpoints for managing products in the system. All endpoints follow RESTful conventions and return JSON responses.

### Features

- ✅ **Pagination**: Efficient handling of large product lists
- ✅ **Filtering**: Search by SKU, name, or active status
- ✅ **Case-insensitive**: SKU searches are case-insensitive
- ✅ **Validation**: Comprehensive input validation with Pydantic
- ✅ **Background Tasks**: Bulk operations via Celery
- ✅ **Clean Architecture**: Layered design (Routes → Services → Repositories)

---

## Base URL

```
http://localhost:8000/api/v1
```

All endpoints are prefixed with `/products`.

---

## Authentication

Currently, no authentication is required. In production, implement JWT or OAuth2.

---

## Endpoints

### 1. List Products

Get a paginated list of products with optional filtering.

**Endpoint:** `GET /products`

**Query Parameters:**

| Parameter | Type    | Required | Default | Description                                      |
|-----------|---------|----------|---------|--------------------------------------------------|
| `limit`   | integer | No       | 20      | Number of items per page (1-100)                |
| `offset`  | integer | No       | 0       | Number of items to skip                          |
| `sku`     | string  | No       | -       | Filter by SKU (partial, case-insensitive match) |
| `name`    | string  | No       | -       | Filter by name (partial, case-insensitive)      |
| `active`  | boolean | No       | -       | Filter by active status (true/false)            |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "sku": "WIDGET-001",
      "name": "Premium Widget",
      "description": "High-quality widget",
      "active": true,
      "created_at": "2025-11-26T15:00:00Z",
      "updated_at": "2025-11-26T15:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

**Example Requests:**

```bash
# Get first 10 products
curl "http://localhost:8000/api/v1/products?limit=10&offset=0"

# Search by SKU
curl "http://localhost:8000/api/v1/products?sku=WIDGET"

# Filter active products
curl "http://localhost:8000/api/v1/products?active=true"

# Combine filters
curl "http://localhost:8000/api/v1/products?name=premium&active=true&limit=5"
```

---

### 2. Get Product by ID

Retrieve a single product by its UUID.

**Endpoint:** `GET /products/{product_id}`

**Path Parameters:**

| Parameter    | Type | Required | Description   |
|--------------|------|----------|---------------|
| `product_id` | UUID | Yes      | Product UUID  |

**Response:** `200 OK`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "sku": "WIDGET-001",
  "name": "Premium Widget",
  "description": "High-quality widget",
  "active": true,
  "created_at": "2025-11-26T15:00:00Z",
  "updated_at": "2025-11-26T15:00:00Z"
}
```

**Errors:**

- `404 Not Found`: Product does not exist

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/products/123e4567-e89b-12d3-a456-426614174000"
```

---

### 3. Create Product

Create a new product.

**Endpoint:** `POST /products`

**Request Body:**

```json
{
  "sku": "WIDGET-001",
  "name": "Premium Widget",
  "description": "High-quality widget for professionals",
  "active": true
}
```

**Field Validation:**

| Field         | Type    | Required | Constraints                          |
|---------------|---------|----------|--------------------------------------|
| `sku`         | string  | Yes      | 1-100 characters, unique (case-insensitive) |
| `name`        | string  | Yes      | 1-255 characters                     |
| `description` | string  | No       | Any length, nullable                 |
| `active`      | boolean | No       | Default: `true`                      |

**Response:** `201 Created`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "sku": "WIDGET-001",
  "name": "Premium Widget",
  "description": "High-quality widget for professionals",
  "active": true,
  "created_at": "2025-11-26T15:00:00Z",
  "updated_at": "2025-11-26T15:00:00Z"
}
```

**Errors:**

- `400 Bad Request`: Invalid input data
- `409 Conflict`: SKU already exists (case-insensitive)

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "WIDGET-001",
    "name": "Premium Widget",
    "description": "High-quality widget",
    "active": true
  }'
```

---

### 4. Update Product

Update an existing product. Only fields provided in the request will be updated (partial update).

**Endpoint:** `PUT /products/{product_id}`

**Path Parameters:**

| Parameter    | Type | Required | Description   |
|--------------|------|----------|---------------|
| `product_id` | UUID | Yes      | Product UUID  |

**Request Body:**

```json
{
  "name": "Updated Widget Name",
  "description": "Updated description",
  "active": false
}
```

**All fields are optional** (partial update supported).

**Response:** `200 OK`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "sku": "WIDGET-001",
  "name": "Updated Widget Name",
  "description": "Updated description",
  "active": false,
  "created_at": "2025-11-26T15:00:00Z",
  "updated_at": "2025-11-26T16:00:00Z"
}
```

**Errors:**

- `400 Bad Request`: Invalid input data
- `404 Not Found`: Product does not exist
- `409 Conflict`: New SKU already exists (if updating SKU)

**Example Request:**

```bash
curl -X PUT "http://localhost:8000/api/v1/products/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Widget Name",
    "active": false
  }'
```

---

### 5. Delete Product

Delete a single product by its UUID.

**Endpoint:** `DELETE /products/{product_id}`

**Path Parameters:**

| Parameter    | Type | Required | Description   |
|--------------|------|----------|---------------|
| `product_id` | UUID | Yes      | Product UUID  |

**Response:** `204 No Content`

No response body.

**Errors:**

- `404 Not Found`: Product does not exist

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/products/123e4567-e89b-12d3-a456-426614174000"
```

---

### 6. Bulk Delete All Products

Delete all products in the database as a background Celery task.

⚠️ **WARNING**: This operation cannot be undone!

**Endpoint:** `DELETE /products/all`

**Response:** `200 OK`

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "submitted",
  "message": "Bulk delete task submitted. Use task ID to monitor progress."
}
```

**Example Request:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/products/all"
```

**Why Celery?**

Bulk delete is performed asynchronously to:
- Avoid blocking the API for large datasets
- Provide progress tracking
- Enable retry logic on failures
- Ensure proper transaction handling

---

### 7. Get Bulk Delete Status

Check the progress of a bulk delete operation.

**Endpoint:** `GET /products/delete/{task_id}/status`

**Path Parameters:**

| Parameter | Type   | Required | Description        |
|-----------|--------|----------|--------------------|
| `task_id` | string | Yes      | Celery task ID     |

**Response:** `200 OK`

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "message": "Successfully deleted 1000 products",
  "percent": 100,
  "deleted_count": 1000,
  "error": null
}
```

**Status Values:**

| Status      | Description                                |
|-------------|--------------------------------------------|
| `PENDING`   | Task is queued and waiting to start       |
| `PROGRESS`  | Task is currently running                  |
| `SUCCESS`   | Task completed successfully                |
| `FAILURE`   | Task encountered an error                  |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/products/delete/abc123-def456-ghi789/status"
```

---

## Schemas

### ProductCreate

```typescript
{
  sku: string;          // 1-100 chars, required
  name: string;         // 1-255 chars, required
  description?: string; // optional
  active?: boolean;     // default: true
}
```

### ProductUpdate

```typescript
{
  sku?: string;         // 1-100 chars, optional
  name?: string;        // 1-255 chars, optional
  description?: string; // optional
  active?: boolean;     // optional
}
```

### ProductResponse

```typescript
{
  id: UUID;
  sku: string;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;   // ISO 8601 datetime
  updated_at: string;   // ISO 8601 datetime
}
```

### ProductListResponse

```typescript
{
  items: ProductResponse[];
  total: number;        // Total count matching filters
  limit: number;        // Items per page
  offset: number;       // Items skipped
  has_more: boolean;    // Whether more items exist
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning                | When It Occurs                          |
|------|------------------------|-----------------------------------------|
| 200  | OK                     | Successful GET/PUT request              |
| 201  | Created                | Successful POST (create) request        |
| 204  | No Content             | Successful DELETE request               |
| 400  | Bad Request            | Invalid input data (validation failed)  |
| 404  | Not Found              | Resource does not exist                 |
| 409  | Conflict               | Duplicate SKU (case-insensitive)        |
| 422  | Unprocessable Entity   | Pydantic validation error               |
| 500  | Internal Server Error  | Unexpected server error                 |

### Validation Errors

Pydantic validation errors return detailed field-level errors:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

---

## Examples

### Complete CRUD Workflow

```bash
# 1. Create a product
PRODUCT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "DEMO-001",
    "name": "Demo Product",
    "description": "This is a demo",
    "active": true
  }' | jq -r '.id')

echo "Created product: $PRODUCT_ID"

# 2. Get the product
curl "http://localhost:8000/api/v1/products/$PRODUCT_ID" | jq '.'

# 3. Update the product
curl -X PUT "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Demo Product",
    "active": false
  }' | jq '.'

# 4. List all products
curl "http://localhost:8000/api/v1/products?limit=10" | jq '.'

# 5. Delete the product
curl -X DELETE "http://localhost:8000/api/v1/products/$PRODUCT_ID" -w "\nStatus: %{http_code}\n"

# 6. Verify deletion (should return 404)
curl "http://localhost:8000/api/v1/products/$PRODUCT_ID"
```

### Pagination Example

```bash
# Get page 1 (first 20 items)
curl "http://localhost:8000/api/v1/products?limit=20&offset=0" | jq '.'

# Get page 2 (next 20 items)
curl "http://localhost:8000/api/v1/products?limit=20&offset=20" | jq '.'

# Get page 3 (next 20 items)
curl "http://localhost:8000/api/v1/products?limit=20&offset=40" | jq '.'
```

### Filtering Examples

```bash
# Find all products with "widget" in the SKU
curl "http://localhost:8000/api/v1/products?sku=widget" | jq '.items[] | {sku, name}'

# Find all inactive products
curl "http://localhost:8000/api/v1/products?active=false" | jq '.items[] | {sku, name, active}'

# Complex filter: active products with "premium" in the name
curl "http://localhost:8000/api/v1/products?name=premium&active=true&limit=5" | jq '.'
```

### Bulk Delete Example

```bash
# Initiate bulk delete
TASK_ID=$(curl -s -X DELETE "http://localhost:8000/api/v1/products/all" | jq -r '.task_id')

echo "Bulk delete task: $TASK_ID"

# Wait 2 seconds
sleep 2

# Check status
curl "http://localhost:8000/api/v1/products/delete/$TASK_ID/status" | jq '.'

# Verify all products deleted
curl "http://localhost:8000/api/v1/products?limit=10" | jq '.total'
```

---

## Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│          API Routes Layer               │
│  (product_routes.py)                    │
│  - Request validation                   │
│  - Response formatting                  │
│  - HTTP concerns                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Service Layer                   │
│  (product_service.py)                   │
│  - Business logic                       │
│  - Validation rules                     │
│  - Transaction management               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Repository Layer                 │
│  (product_repository.py)                │
│  - Database queries                     │
│  - ORM interactions                     │
│  - Data access patterns                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database Layer                  │
│  (PostgreSQL + SQLAlchemy)              │
│  - Data persistence                     │
│  - Constraints                          │
│  - Indexes                              │
└─────────────────────────────────────────┘
```

### Benefits

- ✅ **Separation of Concerns**: Each layer has a single responsibility
- ✅ **Testability**: Easy to unit test each layer independently
- ✅ **Maintainability**: Changes in one layer don't affect others
- ✅ **Scalability**: Easy to add new features or modify existing ones

---

## Testing

A comprehensive test script is provided: `test_crud.sh`

```bash
chmod +x test_crud.sh
./test_crud.sh
```

### Test Coverage

- ✅ Create product
- ✅ Get product by ID
- ✅ List products with pagination
- ✅ Filter by SKU
- ✅ Filter by name
- ✅ Filter by active status
- ✅ Update product
- ✅ Delete product
- ✅ Duplicate SKU rejection (409)
- ✅ Bulk delete via Celery
- ✅ Bulk delete status check

---

## Performance Considerations

### Database Indexes

The `products` table has the following indexes:

- **Primary Key**: `id` (UUID)
- **Unique Index**: `func.lower(sku)` - Case-insensitive SKU uniqueness
- **Composite Index**: `(active, created_at DESC)` - Efficient filtering and sorting

### Pagination

- Always use `limit` to avoid fetching large result sets
- Combine `offset` with `created_at` ordering for consistent pagination
- Maximum limit is 100 to prevent excessive memory usage

### Bulk Operations

- Bulk delete runs as a Celery task to avoid blocking the API
- Progress tracking via Redis for real-time updates
- Automatic retry on failures (max 2 retries)

---

## Future Enhancements

### Planned Features

1. **Batch Create**: `POST /products/batch` - Create multiple products at once
2. **Batch Update**: `PATCH /products/batch` - Update multiple products
3. **Soft Delete**: Add `deleted_at` field instead of hard deletes
4. **Versioning**: Track product history with a `product_versions` table
5. **Full-Text Search**: PostgreSQL `tsvector` for advanced search
6. **Export**: `GET /products/export?format=csv` - Export products
7. **Audit Log**: Track who created/updated/deleted each product

---

## Related Endpoints

- **CSV Import**: `POST /products/upload` - Bulk import via CSV
- **Import Status**: `GET /products/upload/{task_id}/status` - Track CSV import
- **Import Progress**: `GET /products/import/{task_id}/progress` - Detailed progress

---

## Support

For issues or questions:

1. Check the API documentation at `/docs` (Swagger UI)
2. Review the test script: `test_crud.sh`
3. Check logs: `docker-compose logs backend`
4. Open an issue on GitHub

---

**Last Updated**: November 26, 2025  
**API Version**: v1  
**Status**: ✅ Production Ready

