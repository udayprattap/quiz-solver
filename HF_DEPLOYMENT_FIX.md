# 🔧 Hugging Face Space Deployment Fix

**Issue**: Launch timed out after 30 minutes - container not responding to health checks

**Root Cause**: 
1. App running on port **8000** instead of HF Spaces default **7860**
2. Health check pointing to wrong port
3. No startup diagnostics

---

## ✅ Changes Made

### 1. Dockerfile - Port Configuration
**Changed**:
- `EXPOSE 8000` → `EXPOSE 7860`
- `PORT=8000` → `PORT=7860`
- Health check now uses port 7860
- Added startup script for better diagnostics

**Before**:
```dockerfile
EXPOSE 8000
ENV PORT=8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**After**:
```dockerfile
EXPOSE 7860
ENV PORT=7860
CMD ["./start.sh"]
```

### 2. start.sh - Startup Script
**Added**: Comprehensive startup diagnostics
- Environment variable verification
- Playwright availability check
- Port configuration logging
- Clearer error messages

### 3. app.py - Port Flexibility
**Enhanced**: Added `__main__` block for direct execution
- Respects PORT environment variable
- Logs startup port
- Supports both HF Spaces (7860) and local (8000)

---

## 🚀 Deployment Steps

### Method 1: Git Push (Recommended)

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "fix: Change port to 7860 for HF Spaces compatibility

- Update Dockerfile to expose port 7860 (HF default)
- Add start.sh with startup diagnostics
- Enhance health check configuration
- Fix container health probe timeout issue"

# Push to GitHub
git push origin main

# Hugging Face Space will auto-rebuild from GitHub
```

### Method 2: Direct Upload to HF Space

```bash
# Use huggingface-hub CLI
huggingface-cli upload udaypratap/quiz-solver . \
  --repo-type space \
  --exclude ".git/*" ".venv/*" "*.pyc" "__pycache__/*"
```

### Method 3: Web Interface

1. Go to https://huggingface.co/spaces/udaypratap/quiz-solver/tree/main
2. Click "Files" tab
3. Delete old `Dockerfile`, `app.py`, upload new versions
4. Upload new `start.sh`
5. Space will auto-rebuild

---

## 🔍 Verify Deployment

### 1. Check Build Logs
https://huggingface.co/spaces/udaypratap/quiz-solver/logs

**Expected Output**:
```
===== TDS Quiz Solver Startup =====
Timestamp: 2025-11-20 XX:XX:XX
Port: 7860
✅ EMAIL: 24ds3000019@ds.study.iitm.ac.in
✅ SECRET: ***ana
✅ Playwright Chromium: Ready
Starting uvicorn on 0.0.0.0:7860
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### 2. Test Health Endpoint
```bash
curl https://udaypratap-quiz-solver.hf.space/
```

**Expected Response** (HTTP 200):
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "timestamp": "2025-11-20T..."
}
```

### 3. Test Solve Endpoint
```bash
curl -X POST https://udaypratap-quiz-solver.hf.space/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24ds3000019@ds.study.iitm.ac.in",
    "secret": "banana",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

**Expected Response** (HTTP 200):
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: ..."
}
```

---

## 🐛 Troubleshooting

### If Still Times Out

**Option A: Increase Health Check Timeout**

Edit Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD python -c "import requests; requests.get('http://localhost:7860/', timeout=5)" || exit 1
```

**Option B: Add Startup Logs to HF Space Settings**

1. Go to Space Settings
2. Under "Environment Variables", add:
   - `UVICORN_LOG_LEVEL=debug`

**Option C: Simplify Health Check**

Replace health check with simple curl:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
  CMD curl -f http://localhost:7860/ || exit 1
```

(Requires installing curl in Dockerfile: `RUN apt-get update && apt-get install -y curl`)

---

## 📊 Key Changes Summary

| File | Change | Impact |
|------|--------|--------|
| `Dockerfile` | Port 8000 → 7860 | HF Spaces compatibility |
| `Dockerfile` | Added `start.sh` CMD | Better diagnostics |
| `Dockerfile` | Enhanced HEALTHCHECK | Proper health probes |
| `start.sh` | New startup script | Debugging logs |
| `app.py` | Port flexibility | Works locally + HF |

---

## ✅ Expected Timeline

- **Git Push**: ~2-3 minutes
- **HF Space Rebuild**: ~5-8 minutes (Playwright installation)
- **Total**: ~10 minutes from push to live

---

## 🎯 Success Criteria

- ✅ Build completes without errors
- ✅ Health check passes (HTTP 200)
- ✅ `/solve` endpoint accepts requests
- ✅ Background tasks execute
- ✅ Logs show "Application startup complete"

---

**Next Steps**: Push changes to GitHub and monitor HF Space rebuild logs.

**Updated**: 20 November 2025, 14:21 IST
