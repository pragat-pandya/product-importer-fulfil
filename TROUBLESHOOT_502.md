# Troubleshooting 502 Bad Gateway Error

## Quick Diagnostic Commands

Run these commands on your production server to diagnose the issue:

### 1. Check if services are running
```bash
docker-compose ps
```

### 2. Check backend container status
```bash
docker-compose logs --tail=100 backend
```

### 3. Check if backend container is actually running
```bash
docker ps | grep fulfil_backend
```

### 4. Check backend container health
```bash
docker-compose exec backend curl http://localhost:8000/health
```

### 5. Test backend from inside container
```bash
docker-compose exec backend python -c "from app.services.import_service import ImportService; print('OK')"
```

### 6. Check for Python syntax errors
```bash
docker-compose exec backend python -m py_compile app/services/import_service.py
```

### 7. Restart backend service
```bash
docker-compose restart backend
```

### 8. Rebuild and restart (if code changed)
```bash
docker-compose build backend
docker-compose up -d backend
```

## Common Causes and Solutions

### 1. Backend Container Not Running
**Symptoms:** `docker ps` shows no `fulfil_backend` container

**Solution:**
```bash
docker-compose up -d backend
docker-compose logs -f backend
```

### 2. Backend Crashing on Startup
**Symptoms:** Container starts then immediately stops

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
- Import errors (check for recent code changes)
- Database connection issues
- Missing environment variables
- Python syntax errors

**Solution:**
```bash
# Check for import errors
docker-compose exec backend python -c "import app.main"

# Check database connection
docker-compose exec backend python -c "from config import settings; print(settings.DATABASE_URL)"

# Rebuild if code changed
docker-compose build backend
docker-compose up -d backend
```

### 3. Backend Not Listening on Port 8000
**Symptoms:** Container running but no response on port 8000

**Check:**
```bash
docker-compose exec backend netstat -tlnp | grep 8000
# or
docker-compose exec backend ss -tlnp | grep 8000
```

**Solution:**
```bash
# Restart backend
docker-compose restart backend

# Check uvicorn is running
docker-compose exec backend ps aux | grep uvicorn
```

### 4. Nginx/Reverse Proxy Configuration
**Symptoms:** 502 from nginx, backend container is healthy

**Check nginx logs:**
```bash
# If using nginx
tail -f /var/log/nginx/error.log
```

**Check nginx upstream:**
- Ensure nginx is pointing to correct backend URL
- Check if backend port is accessible from nginx container/host

### 5. Recent Code Changes Causing Import Errors
**Symptoms:** 502 after deploying new code

**Check for syntax/import errors:**
```bash
# Test imports
docker-compose exec backend python -c "from app.services.import_service import ImportService"

# Check for syntax errors
docker-compose exec backend python -m py_compile app/services/import_service.py
docker-compose exec backend python -m py_compile app/main.py
```

**Solution:**
```bash
# Rebuild container
docker-compose build backend
docker-compose up -d backend
```

## Full Service Restart

If nothing else works, restart all services:

```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

## Check Service Dependencies

Ensure dependencies are healthy:

```bash
# Check database
docker-compose exec postgres pg_isready -U fulfil_user

# Check Redis
docker-compose exec redis redis-cli ping
```

## Production-Specific Checks

### Environment Variables
```bash
docker-compose exec backend env | grep -E "(DATABASE_URL|REDIS_URL|ENVIRONMENT)"
```

### Resource Limits
```bash
docker stats fulfil_backend
```

### Disk Space
```bash
df -h
docker system df
```

## Quick Fix Script

Run the diagnostic script:
```bash
./scripts/check_backend_health.sh
```

## If Backend Keeps Crashing

1. **Check recent changes:**
   ```bash
   git log --oneline -10
   git diff HEAD~1 backend/
   ```

2. **Revert to last working version:**
   ```bash
   git checkout HEAD~1 backend/app/services/import_service.py
   docker-compose build backend
   docker-compose up -d backend
   ```

3. **Check for memory issues:**
   ```bash
   docker stats
   ```

## Contact Points

- Check application logs: `docker-compose logs -f backend`
- Check system logs: `journalctl -u docker` (if using systemd)
- Check nginx logs: `/var/log/nginx/error.log`

