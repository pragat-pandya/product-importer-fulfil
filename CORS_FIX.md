# CORS Configuration Fix

## Problem
Frontend at `https://fulfil.buzzline.dev` is blocked by CORS when calling backend at `https://fulfil.api.buzzline.dev`

## Solution

### On Server - Run These Commands:

```bash
cd /var/www/fulFil

# 1. Backup .env
cp .env .env.backup

# 2. Remove old CORS_ORIGINS line
sed -i '/^CORS_ORIGINS=/d' .env

# 3. Add correct CORS_ORIGINS (JSON array format)
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env

# 4. Verify
cat .env | grep CORS_ORIGINS

# Should show:
# CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]

# 5. Restart backend
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

# 6. Wait for startup
sleep 10

# 7. Verify backend sees CORS_ORIGINS
docker-compose exec backend python -c "from config import settings; import json; print(json.dumps(settings.CORS_ORIGINS))"
```

### Or Use the Fix Script:

```bash
cd /var/www/fulFil
chmod +x fix_cors.sh
./fix_cors.sh
```

## Test CORS

```bash
# Test preflight request
curl -i -X OPTIONS \
  -H "Origin: https://fulfil.buzzline.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://fulfil.api.buzzline.dev/api/v1/products/upload

# Should return headers:
# Access-Control-Allow-Origin: https://fulfil.buzzline.dev
# Access-Control-Allow-Methods: *
# Access-Control-Allow-Headers: *
```

## Verify in Browser

1. Open https://fulfil.buzzline.dev
2. Clear cache: Cmd+Shift+R or Ctrl+F5
3. Open browser DevTools → Network tab
4. Try uploading a CSV file
5. Check response headers include `Access-Control-Allow-Origin: https://fulfil.buzzline.dev`

## Troubleshooting

If still not working:

```bash
# Check what backend sees
docker-compose exec backend python -c "from config import settings; import json; print('CORS_ORIGINS:', json.dumps(settings.CORS_ORIGINS))"

# Check backend logs
docker-compose logs backend | tail -50

# Test direct API call
curl https://fulfil.api.buzzline.dev/api/v1/hello
```

