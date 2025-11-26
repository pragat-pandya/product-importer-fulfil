# Webhook System - Quick Start Guide

⚡ Get started with webhooks in 5 minutes

---

## 1. Create a Webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhook",
    "events": ["product.created", "product.updated"],
    "secret": "your-secret-key",
    "description": "My webhook",
    "is_active": true
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "url": "https://your-domain.com/webhook",
  "events": ["product.created", "product.updated"],
  "is_active": true,
  "success_count": 0,
  "failure_count": 0
}
```

---

## 2. Test Your Webhook

```bash
WEBHOOK_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST "http://localhost:8000/api/v1/webhooks/$WEBHOOK_ID/test" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "product.created",
    "payload": {
      "id": "test-123",
      "sku": "TEST-001",
      "name": "Test Product"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "response_time_ms": 145,
  "response_body": "{\"status\": \"ok\"}",
  "error": null
}
```

---

## 3. Receive Webhooks

### Expected Payload Format

```json
{
  "event": "product.created",
  "timestamp": "2025-11-26T17:00:00Z",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "sku": "WIDGET-001",
    "name": "Premium Widget",
    "description": "A premium widget",
    "active": true,
    "created_at": "2025-11-26T17:00:00Z"
  }
}
```

### Expected Headers

```http
POST /webhook HTTP/1.1
Host: your-domain.com
Content-Type: application/json
User-Agent: FulFil-Webhook/1.0
X-Webhook-Event: product.created
X-Webhook-Signature: sha256=abc123... (if secret configured)
```

---

## 4. Verify Signature (Recommended)

### Python (FastAPI)

```python
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()
WEBHOOK_SECRET = "your-secret-key"

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_webhook_signature: str = Header(..., alias="X-Webhook-Signature")
):
    # Get raw body
    body = await request.body()
    
    # Verify signature
    expected = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if x_webhook_signature != f"sha256={expected}":
        raise HTTPException(401, "Invalid signature")
    
    # Process webhook
    payload = await request.json()
    print(f"Event: {payload['event']}")
    
    return {"status": "ok"}
```

### Node.js (Express)

```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
const WEBHOOK_SECRET = 'your-secret-key';

app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
  // Get signature from header
  const signature = req.headers['x-webhook-signature'];
  
  // Calculate expected signature
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  hmac.update(req.body);
  const expected = `sha256=${hmac.digest('hex')}`;
  
  // Verify signature
  if (signature !== expected) {
    return res.status(401).json({error: 'Invalid signature'});
  }
  
  // Process webhook
  const payload = JSON.parse(req.body);
  console.log(`Event: ${payload.event}`);
  
  res.json({status: 'ok'});
});

app.listen(8001);
```

---

## 5. Available Events

| Event | Description | Payload |
|-------|-------------|---------|
| `product.created` | Product created | id, sku, name, description, active, created_at |
| `product.updated` | Product updated | id, sku, name, description, active, updated_at |
| `product.deleted` | Product deleted | id, sku, name |
| `import.started` | CSV import started | task_id, filename, total_rows |
| `import.completed` | CSV import completed | task_id, created, updated, errors |
| `import.failed` | CSV import failed | task_id, error |

---

## 6. Check Webhook Logs

```bash
WEBHOOK_ID="123e4567-e89b-12d3-a456-426614174000"

curl "http://localhost:8000/api/v1/webhooks/$WEBHOOK_ID/logs?limit=10"
```

**Response:**
```json
[
  {
    "id": "...",
    "webhook_id": "...",
    "event": "product.created",
    "status_code": 200,
    "response_time_ms": 145,
    "error": null,
    "created_at": "2025-11-26T17:00:00Z"
  }
]
```

---

## 7. Update Webhook

```bash
WEBHOOK_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X PUT "http://localhost:8000/api/v1/webhooks/$WEBHOOK_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "description": "Temporarily disabled"
  }'
```

---

## 8. Testing with webhook.site

1. Go to https://webhook.site
2. Copy your unique URL
3. Create webhook:

```bash
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://webhook.site/YOUR-UNIQUE-ID",
    "events": ["product.created"],
    "is_active": true
  }'
```

4. Create a product in FulFil
5. See the webhook delivery in real-time on webhook.site

---

## 9. Local Testing with Example Receiver

```bash
# Terminal 1: Start example receiver
python examples/webhook_receiver.py

# Terminal 2: Create webhook pointing to local receiver
curl -X POST http://localhost:8000/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://host.docker.internal:8001/webhook",
    "events": ["product.created", "product.updated"],
    "secret": "super-secret-key",
    "is_active": true
  }'

# Terminal 2: Create a product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-001",
    "name": "Test Product",
    "active": true
  }'

# Terminal 1: Watch for incoming webhook!
```

---

## 10. Common Issues

### Webhook Not Triggering
- ✅ Check webhook is `is_active: true`
- ✅ Verify event is in webhook's `events` array
- ✅ Check Celery worker is running: `docker-compose logs worker`

### Signature Verification Failing
- ✅ Use raw body bytes for signature calculation
- ✅ Format: `sha256=<hex_digest>`
- ✅ Use HMAC SHA256, not plain SHA256

### Timeouts
- ✅ Default timeout: 30 seconds
- ✅ Increase with `timeout_seconds` field (max 300)
- ✅ Optimize your webhook endpoint response time

### Testing from Docker
- ✅ Use `http://host.docker.internal:PORT` for localhost endpoints
- ✅ Or deploy receiver to public URL (ngrok, webhook.site, etc.)

---

## 📚 More Resources

- **Full Documentation:** [WEBHOOK_SYSTEM.md](./WEBHOOK_SYSTEM.md)
- **Example Receiver:** [examples/webhook_receiver.py](./examples/webhook_receiver.py)
- **Test Script:** [scripts/test_webhooks.sh](./scripts/test_webhooks.sh)
- **API Docs:** http://localhost:8000/api/docs

---

## 🚀 Quick Commands

```bash
# List all webhooks
curl "http://localhost:8000/api/v1/webhooks"

# Get webhook stats
curl "http://localhost:8000/api/v1/webhooks/{id}"

# Test webhook
curl -X POST "http://localhost:8000/api/v1/webhooks/{id}/test" \
  -H "Content-Type: application/json" \
  -d '{"event":"product.created","payload":{}}'

# View logs
curl "http://localhost:8000/api/v1/webhooks/{id}/logs"

# Disable webhook
curl -X PUT "http://localhost:8000/api/v1/webhooks/{id}" \
  -H "Content-Type: application/json" \
  -d '{"is_active":false}'

# Delete webhook
curl -X DELETE "http://localhost:8000/api/v1/webhooks/{id}"
```

---

**Happy Webhooking! 🎉**

