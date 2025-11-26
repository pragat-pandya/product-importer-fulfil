# 502 Bad Gateway - Debugging Guide

## Quick Diagnostics (Run on Server)

```bash
# 1. Check if backend container is running
docker-compose ps

# Expected: fulfil_backend should show "Up"
# If not running, backend crashed or didn't start

# 2. Check backend logs for errors
docker-compose logs backend --tail=50

# Look for:
# - Port binding errors
# - Database connection errors
# - Import errors
# - Uvicorn startup messages

# 3. Test if backend is responding locally
curl http://localhost:8000/api/v1/hello

# Expected: {"message":"Hello from FulFil Product Importer API!"}
# If this fails, backend isn't running properly

# 4. Check Nginx error logs
sudo tail -50 /var/log/nginx/error.log

# Look for:
# - Connection refused
# - Timeout errors
# - Upstream errors

# 5. Verify Nginx config
sudo nginx -t

# Expected: syntax is ok
```

---

## Common Causes & Fixes

### **Cause 1: Backend Container Not Running**

```bash
# Check container status
docker-compose ps backend

# If it shows "Exit" or not running:
docker-compose logs backend --tail=100

# Restart backend
docker-compose restart backend

# Or rebuild if needed
docker-compose up -d --build backend
```

### **Cause 2: Database Connection Failed**

```bash
# Check if backend can connect to database
docker-compose logs backend | grep -i "database\|postgres\|connection"

# If you see connection errors:
# 1. Check if postgres is running
docker-compose ps postgres

# 2. Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Should be:
# DATABASE_URL=postgresql+asyncpg://fulfil_user:YOUR_PASSWORD@postgres:5432/fulfil_db
```

### **Cause 3: Port Mismatch**

```bash
# Verify backend is listening on port 8000
docker-compose exec backend netstat -tlnp | grep 8000

# Or check from host
curl http://localhost:8000/api/v1/hello

# If port 8000 doesn't respond:
# Check docker-compose.yml ports mapping
grep -A 5 "backend:" docker-compose.yml
```

### **Cause 4: Wrong CORS or Environment**

```bash
# Check backend environment variables
docker-compose exec backend env | grep -E "DATABASE_URL|REDIS_URL|ENVIRONMENT|CORS"

# Verify CORS_ORIGINS includes your domain
# Should have: ["https://fulfil.buzzline.dev","http://fulfil.buzzline.dev"]
```

### **Cause 5: Nginx Config Error**

```bash
# Check Nginx backend config
sudo cat /etc/nginx/sites-available/fulfil-api

# Verify proxy_pass points to correct location:
# Should be: proxy_pass http://localhost:8000;

# Test Nginx config
sudo nginx -t

# If config is OK, reload
sudo systemctl reload nginx
```

---

## Step-by-Step Fix

### **Step 1: Verify Backend is Running**

```bash
cd ~/fulFil

# Check all containers
docker-compose ps

# Output should show:
# fulfil_backend    Up      0.0.0.0:8000->8000/tcp
# fulfil_postgres   Up      0.0.0.0:5433->5432/tcp
# fulfil_redis      Up      0.0.0.0:6379->6379/tcp
# fulfil_worker     Up
```

### **Step 2: Check Backend Logs**

```bash
# View recent logs
docker-compose logs backend --tail=100 -f

# Look for startup message:
# "Application startup complete"
# "Uvicorn running on http://0.0.0.0:8000"

# If you see errors, read them carefully
# Common errors:
# - ModuleNotFoundError: Missing Python package
# - psycopg2.OperationalError: Database connection failed
# - ValueError: Invalid DATABASE_URL
```

### **Step 3: Test Backend Locally**

```bash
# Test from server command line
curl http://localhost:8000/api/v1/hello

# Expected response:
# {"message":"Hello from FulFil Product Importer API!"}

# If this works, backend is fine, issue is with Nginx
# If this fails, backend has a problem
```

### **Step 4: Check Nginx Configuration**

```bash
# View Nginx config for API
sudo cat /etc/nginx/sites-available/fulfil-api

# Important lines should be:
# server_name fulfil.api.buzzline.dev;
# proxy_pass http://localhost:8000;

# Test config syntax
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### **Step 5: Restart Everything (If Needed)**

```bash
cd ~/fulFil

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Wait 10 seconds for startup
sleep 10

# Check status
docker-compose ps

# Test backend
curl http://localhost:8000/api/v1/hello

# Test through Nginx
curl http://localhost/api/v1/hello
# (This tests Nginx -> Backend)
```

---

## Quick Fix Commands

```bash
# If backend container is down:
docker-compose restart backend

# If backend has errors:
docker-compose logs backend --tail=100

# If database connection fails:
docker-compose restart postgres
docker-compose restart backend

# If Nginx has issues:
sudo nginx -t
sudo systemctl reload nginx

# Nuclear option (restart everything):
cd ~/fulFil
docker-compose down
docker-compose up -d
sleep 10
docker-compose ps
curl http://localhost:8000/api/v1/hello
```

---

## Verify Everything Works

```bash
# 1. Backend responds locally
curl http://localhost:8000/api/v1/hello

# 2. Nginx can reach backend (HTTP)
curl http://localhost/api/v1/hello

# 3. HTTPS works (if SSL is setup)
curl https://fulfil.api.buzzline.dev/api/v1/hello

# 4. API docs accessible
curl https://fulfil.api.buzzline.dev/api/docs
# Should return HTML

# 5. Check all services are healthy
docker-compose ps
# All should show "Up"
```

---

## Most Likely Issues

### **Issue 1: Backend Didn't Start**

**Symptoms:** 
- `docker-compose ps` shows backend as "Exit 1" or not running
- Logs show Python errors

**Fix:**
```bash
# View full logs
docker-compose logs backend

# Common fixes:
# - Missing .env file: Create .env with DATABASE_URL
# - Wrong DATABASE_URL: Fix in .env
# - Missing Python package: Rebuild image
docker-compose build backend
docker-compose up -d backend
```

### **Issue 2: Database Connection Failed**

**Symptoms:**
- Backend starts but logs show "could not connect to server"
- asyncpg.exceptions errors

**Fix:**
```bash
# Check postgres is running
docker-compose ps postgres

# If postgres is on different port (5433):
# Make sure DATABASE_URL uses @postgres:5432 (internal port)
# Example: postgresql+asyncpg://user:pass@postgres:5432/fulfil_db

# Restart both
docker-compose restart postgres backend
```

### **Issue 3: Port Already in Use**

**Symptoms:**
- Error: "address already in use"
- Backend won't start

**Fix:**
```bash
# Check what's using port 8000
sudo lsof -i :8000

# If another process is using it:
# Option 1: Kill that process
sudo kill -9 <PID>

# Option 2: Change backend port in docker-compose.yml
# Change: "8000:8000" to "8001:8000"
# Update Nginx config to proxy_pass http://localhost:8001;
```

---

## Get Help

If none of these work, run this diagnostic script:

```bash
#!/bin/bash
echo "=== FulFil 502 Diagnostic ==="
echo ""
echo "1. Docker Container Status:"
docker-compose ps
echo ""
echo "2. Backend Logs (last 20 lines):"
docker-compose logs backend --tail=20
echo ""
echo "3. Nginx Error Logs:"
sudo tail -20 /var/log/nginx/error.log
echo ""
echo "4. Test Backend Locally:"
curl -s http://localhost:8000/api/v1/hello || echo "FAILED"
echo ""
echo "5. Port 8000 Status:"
sudo lsof -i :8000 || echo "Nothing on port 8000"
echo ""
echo "6. Environment Variables:"
docker-compose exec backend env | grep -E "DATABASE|REDIS|ENVIRONMENT"
```

Save this as `debug.sh`, run `chmod +x debug.sh`, then `./debug.sh` and share the output.

