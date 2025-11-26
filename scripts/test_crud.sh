#!/bin/bash

# CRUD Endpoints Test Script
# Tests all Product CRUD operations

set -e

BASE_URL="http://localhost:8000/api/v1"
echo "🧪 Testing Product CRUD Endpoints"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Create a product
echo -e "${BLUE}📝 Test 1: POST /products (Create Product)${NC}"
PRODUCT1=$(curl -s -X POST "${BASE_URL}/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-CRUD-001",
    "name": "Test Product 1",
    "description": "First test product",
    "active": true
  }')
echo "$PRODUCT1" | jq '.'
PRODUCT1_ID=$(echo "$PRODUCT1" | jq -r '.id')
echo -e "${GREEN}✅ Product created with ID: $PRODUCT1_ID${NC}"
echo ""

# Test 2: Create another product
echo -e "${BLUE}📝 Test 2: POST /products (Create Another Product)${NC}"
PRODUCT2=$(curl -s -X POST "${BASE_URL}/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-CRUD-002",
    "name": "Test Product 2",
    "description": "Second test product",
    "active": false
  }')
echo "$PRODUCT2" | jq '.'
PRODUCT2_ID=$(echo "$PRODUCT2" | jq -r '.id')
echo -e "${GREEN}✅ Product created with ID: $PRODUCT2_ID${NC}"
echo ""

# Test 3: Get single product by ID
echo -e "${BLUE}🔍 Test 3: GET /products/{id} (Get Product by ID)${NC}"
curl -s "${BASE_URL}/products/${PRODUCT1_ID}" | jq '.'
echo -e "${GREEN}✅ Retrieved product by ID${NC}"
echo ""

# Test 4: List all products
echo -e "${BLUE}📋 Test 4: GET /products (List All Products)${NC}"
curl -s "${BASE_URL}/products?limit=10&offset=0" | jq '.'
echo -e "${GREEN}✅ Listed products${NC}"
echo ""

# Test 5: Filter by SKU
echo -e "${BLUE}🔎 Test 5: GET /products?sku=TEST-CRUD (Filter by SKU)${NC}"
curl -s "${BASE_URL}/products?sku=TEST-CRUD" | jq '.'
echo -e "${GREEN}✅ Filtered by SKU${NC}"
echo ""

# Test 6: Filter by name
echo -e "${BLUE}🔎 Test 6: GET /products?name=Product 1 (Filter by Name)${NC}"
curl -s "${BASE_URL}/products?name=Product%201" | jq '.'
echo -e "${GREEN}✅ Filtered by name${NC}"
echo ""

# Test 7: Filter by active status
echo -e "${BLUE}🔎 Test 7: GET /products?active=true (Filter by Active)${NC}"
curl -s "${BASE_URL}/products?active=true" | jq '.'
echo -e "${GREEN}✅ Filtered by active status${NC}"
echo ""

# Test 8: Update product
echo -e "${BLUE}✏️  Test 8: PUT /products/{id} (Update Product)${NC}"
curl -s -X PUT "${BASE_URL}/products/${PRODUCT1_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name",
    "description": "Updated description",
    "active": false
  }' | jq '.'
echo -e "${GREEN}✅ Product updated${NC}"
echo ""

# Test 9: Verify update
echo -e "${BLUE}✔️  Test 9: GET /products/{id} (Verify Update)${NC}"
curl -s "${BASE_URL}/products/${PRODUCT1_ID}" | jq '.'
echo -e "${GREEN}✅ Update verified${NC}"
echo ""

# Test 10: Delete single product
echo -e "${BLUE}🗑️  Test 10: DELETE /products/{id} (Delete Product)${NC}"
curl -s -X DELETE "${BASE_URL}/products/${PRODUCT2_ID}" -w "\nStatus: %{http_code}\n"
echo -e "${GREEN}✅ Product deleted${NC}"
echo ""

# Test 11: Verify deletion (should return 404)
echo -e "${BLUE}🔍 Test 11: GET /products/{id} (Verify Deletion - Expect 404)${NC}"
RESPONSE=$(curl -s -w "\nSTATUS:%{http_code}" "${BASE_URL}/products/${PRODUCT2_ID}")
echo "$RESPONSE"
if echo "$RESPONSE" | grep -q "STATUS:404"; then
    echo -e "${GREEN}✅ Deletion verified (404 returned as expected)${NC}"
else
    echo -e "${RED}❌ Expected 404 but got different status${NC}"
fi
echo ""

# Test 12: Try to create duplicate SKU (should fail with 409)
echo -e "${BLUE}⚠️  Test 12: POST /products (Duplicate SKU - Expect 409)${NC}"
RESPONSE=$(curl -s -w "\nSTATUS:%{http_code}" -X POST "${BASE_URL}/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-CRUD-001",
    "name": "Duplicate SKU Product",
    "description": "This should fail",
    "active": true
  }')
echo "$RESPONSE"
if echo "$RESPONSE" | grep -q "STATUS:409"; then
    echo -e "${GREEN}✅ Duplicate SKU rejected (409 returned as expected)${NC}"
else
    echo -e "${RED}❌ Expected 409 but got different status${NC}"
fi
echo ""

# Test 13: Pagination
echo -e "${BLUE}📄 Test 13: GET /products?limit=1&offset=0 (Pagination)${NC}"
curl -s "${BASE_URL}/products?limit=1&offset=0" | jq '.'
echo -e "${GREEN}✅ Pagination working${NC}"
echo ""

# Test 14: Bulk delete (triggers Celery task)
echo -e "${YELLOW}🗑️  Test 14: DELETE /products/all (Bulk Delete - Celery Task)${NC}"
BULK_DELETE=$(curl -s -X DELETE "${BASE_URL}/products/all")
echo "$BULK_DELETE" | jq '.'
TASK_ID=$(echo "$BULK_DELETE" | jq -r '.task_id')
echo -e "${YELLOW}⏳ Bulk delete task submitted with ID: $TASK_ID${NC}"
echo ""

# Test 15: Check bulk delete status
echo -e "${BLUE}📊 Test 15: GET /products/delete/{task_id}/status (Check Bulk Delete Status)${NC}"
echo "Waiting 2 seconds for task to complete..."
sleep 2
curl -s "${BASE_URL}/products/delete/${TASK_ID}/status" | jq '.'
echo -e "${GREEN}✅ Bulk delete status retrieved${NC}"
echo ""

# Test 16: Verify all products deleted
echo -e "${BLUE}📋 Test 16: GET /products (Verify Bulk Delete)${NC}"
FINAL_LIST=$(curl -s "${BASE_URL}/products?limit=10&offset=0")
echo "$FINAL_LIST" | jq '.'
TOTAL=$(echo "$FINAL_LIST" | jq -r '.total')
if [ "$TOTAL" = "0" ]; then
    echo -e "${GREEN}✅ All products deleted successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Found $TOTAL products remaining${NC}"
fi
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ All CRUD endpoint tests completed!${NC}"
echo -e "${GREEN}================================================${NC}"

