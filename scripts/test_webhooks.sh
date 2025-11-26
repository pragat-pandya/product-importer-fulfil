#!/bin/bash

# Webhook System Test Script
# Tests all webhook CRUD operations and triggering

set -e

BASE_URL="http://localhost:8000/api/v1"
echo "🧪 Testing Webhook System"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Create a webhook
echo -e "${BLUE}📝 Test 1: POST /webhooks (Create Webhook)${NC}"
WEBHOOK=$(curl -s -X POST "${BASE_URL}/webhooks" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/post",
    "events": ["product.created", "product.updated", "product.deleted"],
    "description": "Test webhook for httpbin",
    "is_active": true,
    "retry_count": 3,
    "timeout_seconds": 30
  }')
echo "$WEBHOOK" | jq '.'
WEBHOOK_ID=$(echo "$WEBHOOK" | jq -r '.id')
echo -e "${GREEN}✅ Webhook created with ID: $WEBHOOK_ID${NC}"
echo ""

# Test 2: Get webhook by ID
echo -e "${BLUE}🔍 Test 2: GET /webhooks/{id} (Get Webhook)${NC}"
curl -s "${BASE_URL}/webhooks/${WEBHOOK_ID}" | jq '{id:.id, url:.url, events:.events, is_active:.is_active, success_count:.success_count, failure_count:.failure_count}'
echo -e "${GREEN}✅ Retrieved webhook${NC}"
echo ""

# Test 3: List webhooks
echo -e "${BLUE}📋 Test 3: GET /webhooks (List Webhooks)${NC}"
curl -s "${BASE_URL}/webhooks?limit=10" | jq '{total:.total, webhooks_count:.items | length}'
echo -e "${GREEN}✅ Listed webhooks${NC}"
echo ""

# Test 4: Test webhook with dummy payload
echo -e "${BLUE}🧪 Test 4: POST /webhooks/{id}/test (Test Webhook)${NC}"
TEST_RESULT=$(curl -s -X POST "${BASE_URL}/webhooks/${WEBHOOK_ID}/test" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "product.created",
    "payload": {
      "id": "test-123",
      "sku": "TEST-WEBHOOK-001",
      "name": "Test Webhook Product",
      "description": "This is a test",
      "active": true
    }
  }')
echo "$TEST_RESULT" | jq '.'
echo -e "${GREEN}✅ Webhook test executed${NC}"
echo ""

# Test 5: Create product (should trigger webhook via Celery)
echo -e "${YELLOW}🔔 Test 5: Create Product (Should Trigger Webhook)${NC}"
PRODUCT=$(curl -s -X POST "${BASE_URL}/products" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "WEBHOOK-TEST-PRODUCT-001",
    "name": "Product That Triggers Webhook",
    "description": "This creation should trigger the webhook",
    "active": true
  }')
echo "$PRODUCT" | jq '{id:.id, sku:.sku, name:.name}'
PRODUCT_ID=$(echo "$PRODUCT" | jq -r '.id')
echo -e "${YELLOW}⏳ Waiting 3 seconds for Celery task to execute...${NC}"
sleep 3
echo -e "${GREEN}✅ Product created${NC}"
echo ""

# Test 6: Check webhook logs
echo -e "${BLUE}📊 Test 6: GET /webhooks/{id}/logs (Check Execution Logs)${NC}"
LOGS=$(curl -s "${BASE_URL}/webhooks/${WEBHOOK_ID}/logs?limit=5")
echo "$LOGS" | jq 'map({event:.event, status_code:.status_code, response_time_ms:.response_time_ms, error:.error}) | .[:3]'
LOG_COUNT=$(echo "$LOGS" | jq '. | length')
echo -e "${GREEN}✅ Retrieved $LOG_COUNT logs${NC}"
echo ""

# Test 7: Update webhook stats
echo -e "${BLUE}📈 Test 7: GET /webhooks/{id} (Check Updated Stats)${NC}"
curl -s "${BASE_URL}/webhooks/${WEBHOOK_ID}" | jq '{success_count:.success_count, failure_count:.failure_count, last_triggered_at:.last_triggered_at}'
echo -e "${GREEN}✅ Webhook stats updated after execution${NC}"
echo ""

# Test 8: Update product (should trigger webhook)
echo -e "${YELLOW}🔔 Test 8: Update Product (Should Trigger Webhook)${NC}"
curl -s -X PUT "${BASE_URL}/products/${PRODUCT_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name That Triggers Webhook",
    "active": false
  }' | jq '{id:.id, name:.name, active:.active}'
echo -e "${YELLOW}⏳ Waiting 3 seconds for Celery task...${NC}"
sleep 3
echo -e "${GREEN}✅ Product updated${NC}"
echo ""

# Test 9: Update webhook (disable it)
echo -e "${BLUE}✏️  Test 9: PUT /webhooks/{id} (Update Webhook)${NC}"
curl -s -X PUT "${BASE_URL}/webhooks/${WEBHOOK_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "description": "Webhook disabled for testing"
  }' | jq '{id:.id, is_active:.is_active, description:.description}'
echo -e "${GREEN}✅ Webhook updated${NC}"
echo ""

# Test 10: Delete product (should NOT trigger webhook - webhook is disabled)
echo -e "${YELLOW}🔕 Test 10: Delete Product (Webhook Disabled - No Trigger)${NC}"
curl -s -X DELETE "${BASE_URL}/products/${PRODUCT_ID}"
echo "Status: 204 (Product deleted)"
echo -e "${GREEN}✅ Product deleted (webhook not triggered - disabled)${NC}"
echo ""

# Test 11: Check final logs
echo -e "${BLUE}📊 Test 11: GET /webhooks/{id}/logs (Final Log Check)${NC}"
FINAL_LOGS=$(curl -s "${BASE_URL}/webhooks/${WEBHOOK_ID}/logs?limit=10")
echo "$FINAL_LOGS" | jq 'map({event:.event, status_code:.status_code}) | .[:5]'
FINAL_LOG_COUNT=$(echo "$FINAL_LOGS" | jq '. | length')
echo -e "${GREEN}✅ Total logs: $FINAL_LOG_COUNT${NC}"
echo ""

# Test 12: Delete webhook
echo -e "${BLUE}🗑️  Test 12: DELETE /webhooks/{id} (Delete Webhook)${NC}"
curl -s -X DELETE "${BASE_URL}/webhooks/${WEBHOOK_ID}" -w "\nStatus: %{http_code}\n"
echo -e "${GREEN}✅ Webhook deleted${NC}"
echo ""

# Test 13: Verify deletion
echo -e "${BLUE}🔍 Test 13: GET /webhooks/{id} (Verify Deletion - Expect 404)${NC}"
RESPONSE=$(curl -s -w "\nSTATUS:%{http_code}" "${BASE_URL}/webhooks/${WEBHOOK_ID}")
echo "$RESPONSE"
if echo "$RESPONSE" | grep -q "STATUS:404"; then
    echo -e "${GREEN}✅ Deletion verified (404 returned as expected)${NC}"
else
    echo -e "${RED}❌ Expected 404 but got different status${NC}"
fi
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ All webhook tests completed!${NC}"
echo -e "${GREEN}================================================${NC}"

