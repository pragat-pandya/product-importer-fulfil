# Complete CORS Fix Guide

## Problem
CORS errors persist because Pydantic Settings isn't parsing JSON arrays from `.env` correctly.

## Solution

### Step 1: Update Backend Config (Already Done Locally)
The `config.py` has been updated to properly parse CORS_ORIGINS. You need to update it on the server.

### Step 2: Update .env File on Server

```bash
# SSH to server
ssh root@fulfil.buzzline.dev

cd /var/www/fulFil

# Backup .env
cp .env .env.backup

# Remove old CORS_ORIGINS
sed -i '/^CORS_ORIGINS=/d' .env

# Add new CORS_ORIGINS (JSON format)
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env

# Verify
cat .env | grep CORS_ORIGINS
```

### Step 3: Update config.py on Server

Copy the updated `backend/config.py` to the server, or manually edit:

```bash
cd /var/www/fulFil

# Backup old config
cp backend/config.py backend/config.py.backup

# Edit config.py
nano backend/config.py
```

**Add these imports at the top:**
```python
import json
from pydantic import field_validator
```

**Add this validator method to the Settings class (after CORS_ORIGINS field):**
```python
@field_validator('CORS_ORIGINS', mode='before')
@classmethod
def parse_cors_origins(cls, v):
    """Parse CORS_ORIGINS from JSON string or comma-separated string"""
    if isinstance(v, str):
        # Try parsing as JSON first
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            # If not JSON, try comma-separated
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            # Single value
            return [v.strip()]
    return v
```

### Step 4: Restart Backend

```bash
cd /var/www/fulFil

# Rebuild backend to pick up config changes
docker-compose build backend

# Restart
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

# Wait for startup
sleep 10

# Check logs
docker-compose logs backend --tail=30
```

### Step 5: Verify CORS is Working

```bash
# Test CORS preflight
curl -i -X OPTIONS \
  -H "Origin: https://fulfil.buzzline.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://fulfil.api.buzzline.dev/api/v1/products/upload

# Should see:
# Access-Control-Allow-Origin: https://fulfil.buzzline.dev
```

### Step 6: Test in Browser

1. Clear browser cache: `Cmd+Shift+R` or `Ctrl+F5`
2. Open: https://fulfil.buzzline.dev
3. Try uploading a CSV
4. Check console - CORS error should be gone!

## Quick One-Line Fix (After updating config.py)

```bash
cd /var/www/fulFil && \
cp .env .env.backup && \
sed -i '/^CORS_ORIGINS=/d' .env && \
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env && \
docker-compose build backend && \
docker-compose restart backend && \
sleep 10 && \
docker-compose logs backend --tail=20
```

## Alternative: Transfer Updated Files

From your local machine:

```bash
cd /Users/pragat/Documents/fulFil

# Transfer updated config.py
scp backend/config.py root@fulfil.buzzline.dev:/var/www/fulFil/backend/

# Then on server, restart
ssh root@fulfil.buzzline.dev
cd /var/www/fulFil
docker-compose build backend
docker-compose restart backend
```

