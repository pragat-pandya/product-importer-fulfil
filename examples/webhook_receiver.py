"""
Example Webhook Receiver
Demonstrates how to receive and verify webhooks from FulFil
"""
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Webhook Receiver Example")

# Your webhook secret (same as configured in FulFil)
WEBHOOK_SECRET = "super-secret-key"


class WebhookPayload(BaseModel):
    """Expected webhook payload structure"""
    event: str
    timestamp: str
    data: Dict[str, Any]


def verify_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC SHA256 signature from FulFil webhook.
    
    Args:
        payload_bytes: Raw request body
        signature: X-Webhook-Signature header value (format: "sha256=<hex>")
        secret: Webhook secret key
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature.startswith("sha256="):
        return False
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    received_signature = signature.split("=", 1)[1]
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected_signature, received_signature)


@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    x_webhook_event: Optional[str] = Header(None, alias="X-Webhook-Event"),
):
    """
    Receive webhook from FulFil.
    
    This endpoint:
    1. Verifies the HMAC signature
    2. Parses the payload
    3. Processes the event
    4. Returns 200 OK
    """
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature if secret is configured
    if WEBHOOK_SECRET and x_webhook_signature:
        if not verify_signature(body, x_webhook_signature, WEBHOOK_SECRET):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )
    
    # Parse JSON payload
    try:
        payload = await request.json()
        webhook_data = WebhookPayload(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid payload: {str(e)}"
        )
    
    # Process event
    event = webhook_data.event
    data = webhook_data.data
    
    print(f"📬 Received webhook: {event}")
    print(f"   Timestamp: {webhook_data.timestamp}")
    print(f"   Data: {data}")
    
    # Handle different event types
    if event == "product.created":
        handle_product_created(data)
    elif event == "product.updated":
        handle_product_updated(data)
    elif event == "product.deleted":
        handle_product_deleted(data)
    elif event == "import.completed":
        handle_import_completed(data)
    elif event == "import.failed":
        handle_import_failed(data)
    else:
        print(f"⚠️  Unknown event type: {event}")
    
    # Return success response
    return {
        "status": "ok",
        "message": f"Webhook received: {event}",
        "event_id": data.get("id"),
    }


def handle_product_created(data: Dict[str, Any]):
    """Handle product.created event"""
    print(f"✅ Product created: {data.get('sku')} - {data.get('name')}")
    
    # Example: Sync to inventory system
    # inventory_api.create_product(data)
    
    # Example: Send notification
    # slack.send_message(f"New product: {data['name']}")
    
    # Example: Update analytics
    # analytics.track("product_created", data)


def handle_product_updated(data: Dict[str, Any]):
    """Handle product.updated event"""
    print(f"✏️  Product updated: {data.get('sku')} - {data.get('name')}")
    
    # Example: Sync updates to external system
    # inventory_api.update_product(data['id'], data)


def handle_product_deleted(data: Dict[str, Any]):
    """Handle product.deleted event"""
    print(f"🗑️  Product deleted: {data.get('sku')}")
    
    # Example: Remove from external system
    # inventory_api.delete_product(data['id'])


def handle_import_completed(data: Dict[str, Any]):
    """Handle import.completed event"""
    print(f"📦 Import completed: {data.get('created')} created, {data.get('updated')} updated")
    
    # Example: Send summary email
    # email.send(f"Import completed: {data['created']} products imported")


def handle_import_failed(data: Dict[str, Any]):
    """Handle import.failed event"""
    print(f"❌ Import failed: {data.get('error')}")
    
    # Example: Send alert
    # pagerduty.trigger_alert(f"Import failed: {data['error']}")


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Webhook Receiver Example",
        "webhook_endpoint": "/webhook"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Webhook Receiver Example")
    print("📬 Webhook endpoint: http://localhost:8001/webhook")
    print("🔐 Secret configured: Yes" if WEBHOOK_SECRET else "⚠️  No secret configured")
    print("")
    print("To test:")
    print("1. Configure webhook in FulFil with URL: http://host.docker.internal:8001/webhook")
    print("2. Create/update/delete products in FulFil")
    print("3. Watch this console for incoming webhooks")
    print("")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

