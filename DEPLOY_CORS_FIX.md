# Deploy CORS Fix - Step by Step

After pulling the latest changes with the CORS fix, follow these steps:

## Step 1: Update .env File on Server

```bash
# SSH to server
ssh root@fulfil.buzzline.dev

cd /var/www/fulFil

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Remove old CORS_ORIGINS line
sed -i '/^CORS_ORIGINS=/d' .env

# Add new CORS_ORIGINS (JSON format)
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env

# Verify
cat .env | grep CORS_ORIGINS
# Should show: CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]
```

## Step 2: Rebuild and Restart Backend

```bash
cd /var/www/fulFil

# Pull latest changes (if using git) - YOU ALREADY DID THIS
# git pull  # Skip if you already pulled

# Rebuild backend to pick up config.py changes
docker-compose build backend

# Restart backend
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

# Wait for startup
sleep 10

# Check status
docker-compose ps backend

# View logs to verify startup
docker-compose logs backend --tail=30
```

## Step 3: Verify CORS Configuration

```bash
# Check what CORS_ORIGINS the backend sees
docker-compose exec backend python -c "from config import settings; import json; print('CORS_ORIGINS:', json.dumps(settings.CORS_ORIGINS))"

# Should output something like:
# CORS_ORIGINS: ["https://fulfil.buzzline.dev", "http://fulfil.buzzline.dev", "https://fulfil.api.buzzline.dev"]
```

## Step 4: Test CORS Headers

```bash
# Test preflight request
curl -i -X OPTIONS \
  -H "Origin: https://fulfil.buzzline.dev" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  https://fulfil.api.buzzline.dev/api/v1/products/upload

# Look for these headers in response:
# Access-Control-Allow-Origin: https://fulfil.buzzline.dev
# Access-Control-Allow-Methods: *
# Access-Control-Allow-Headers: *
```

## Step 5: Test in Browser

1. Open: https://fulfil.buzzline.dev
2. **Clear browser cache** (Cmd+Shift+R on Mac, Ctrl+F5 on Windows)
3. Navigate to Upload page
4. Try uploading a CSV file
5. Check browser console - CORS error should be gone!

## One-Line Command (All Steps)

```bash
cd /var/www/fulFil && \
cp .env .env.backup.$(date +%Y%m%d_%H%M%S) && \
sed -i '/^CORS_ORIGINS=/d' .env && \
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env && \
docker-compose build backend && \
docker-compose stop backend && \
docker-compose rm -f backend && \
docker-compose up -d backend && \
sleep 10 && \
docker-compose logs backend --tail=20 && \
echo "" && \
echo "✅ Testing CORS..." && \
docker-compose exec backend python -c "from config import settings; import json; print('CORS_ORIGINS:', json.dumps(settings.CORS_ORIGINS))"
```

## Troubleshooting

### If CORS still doesn't work:

1. **Check backend logs:**
   ```bash
   docker-compose logs backend | tail -50
   ```

2. **Verify config.py was updated:**
   ```bash
   grep -A 10 "parse_cors_origins" backend/config.py
   # Should show the validator method
   ```

3. **Check .env format:**
   ```bash
   cat .env | grep CORS_ORIGINS
   # Should be: CORS_ORIGINS=["https://fulfil.buzzline.dev",...]
   ```

4. **Force rebuild without cache:**
   ```bash
   docker-compose build --no-cache backend
   docker-compose up -d backend
   ```

## Success Indicators

✅ Backend logs show "Application startup complete"  
✅ `docker-compose exec backend python -c "from config import settings; print(settings.CORS_ORIGINS)"` shows your domains  
✅ curl test shows `Access-Control-Allow-Origin` header  
✅ Browser upload works without CORS errors  

