#!/bin/bash
# Fix CORS Configuration on Server

echo "🔧 Fixing CORS Configuration"
echo "============================"
echo ""

# Backup .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up .env file"
echo ""

# Remove old CORS_ORIGINS line
sed -i '/^CORS_ORIGINS=/d' .env
echo "✅ Removed old CORS_ORIGINS"
echo ""

# Add correct CORS_ORIGINS format
echo 'CORS_ORIGINS=["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev","https://fulfil.api.buzzline.dev"]' >> .env
echo "✅ Added new CORS_ORIGINS"
echo ""

# Show updated .env
echo "Updated .env (CORS section):"
grep CORS_ORIGINS .env
echo ""

# Restart backend
echo "🔄 Restarting backend..."
docker-compose stop backend
docker-compose rm -f backend
docker-compose up -d backend

echo ""
echo "⏳ Waiting 10 seconds for backend to start..."
sleep 10

# Check backend status
echo ""
echo "📊 Backend Status:"
docker-compose ps backend
echo ""

# Check CORS_ORIGINS in container
echo "🔍 Checking CORS_ORIGINS in container:"
docker-compose exec backend python -c "from config import settings; import json; print('CORS_ORIGINS:', json.dumps(settings.CORS_ORIGINS))" 2>/dev/null || echo "Could not check - backend might still be starting"

echo ""
echo "✅ CORS fix complete!"
echo ""
echo "🧪 Test CORS:"
echo "curl -i -X OPTIONS -H 'Origin: https://fulfil.buzzline.dev' -H 'Access-Control-Request-Method: POST' https://fulfil.api.buzzline.dev/api/v1/products/upload"

