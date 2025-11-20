# 🔧 Hugging Face Space Setup Guide

**CRITICAL**: Follow these steps to configure your HF Space properly

---

## Step 1: Verify Repository Sync

Your HF Space should auto-sync from GitHub:
- Go to: https://huggingface.co/spaces/udaypratap/quiz-solver/settings
- Under "Linked Git Repository", verify it shows: `udayprattap/quiz-solver`
- If not linked, connect it now

---

## Step 2: Configure Environment Variables (REQUIRED)

Go to: https://huggingface.co/spaces/udaypratap/quiz-solver/settings

### Add These Secrets:

1. **EMAIL** (Required)
   - Value: `24ds3000019@ds.study.iitm.ac.in`
   - Type: Secret (not public)

2. **SECRET** (Required)
   - Value: `banana`
   - Type: Secret (not public)

3. **PIPE_TOKEN** (Optional but recommended)
   - Value: `eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDE5QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.e-weorC0bDwFYratH3hrojc7XV5C-a0n82jWpn743rE`
   - Type: Secret (not public)
   - Purpose: Enables LLM-enhanced question answering

### Optional Variables:

4. **DISABLE_PLAYWRIGHT**
   - Value: `0` (0=enabled, 1=disabled)
   - Type: Public

5. **RATE_LIMIT_WINDOW**
   - Value: `60` (seconds)
   - Type: Public

6. **RATE_LIMIT_MAX**
   - Value: `10` (requests per window)
   - Type: Public

---

## Step 3: Force Rebuild

After adding environment variables:

1. Go to: https://huggingface.co/spaces/udaypratap/quiz-solver/settings
2. Click "Factory Reboot" button
3. Wait 5-8 minutes for rebuild

---

## Step 4: Verify Deployment

### Check Build Logs
https://huggingface.co/spaces/udaypratap/quiz-solver/logs

**Expected Output**:
```
===== TDS Quiz Solver Startup =====
Port: 7860
✅ EMAIL: 24ds3000019@ds.study.iitm.ac.in
✅ SECRET: ***ana
✅ PIPE_TOKEN: Configured
✅ Playwright Chromium: Ready
Starting uvicorn on 0.0.0.0:7860
INFO:     Uvicorn running on http://0.0.0.0:7860
```

### Test Health Endpoint
```bash
curl https://udaypratap-quiz-solver.hf.space/
```

**Expected Response** (HTTP 200):
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "playwright_enabled": true
}
```

---

## Step 5: Test Solve Endpoint

```bash
curl -X POST https://udaypratap-quiz-solver.hf.space/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "24ds3000019@ds.study.iitm.ac.in",
    "secret": "banana",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

**Expected Response**:
```json
{
  "status": "processing",
  "message": "Quiz solving started for URL: ..."
}
```

---

## Troubleshooting

### Issue: "PIPE_TOKEN not set" in logs

**Solution**: 
1. Go to Space Settings
2. Add `PIPE_TOKEN` as a Secret
3. Click "Factory Reboot"

### Issue: "Launch timed out after 30 min"

**Possible Causes**:
1. Environment variables not configured (see Step 2)
2. Old build still running (port 8000 instead of 7860)
3. Health check failing

**Solution**:
1. Verify all environment variables are set
2. Force Factory Reboot
3. Check build logs for errors

### Issue: Port 8000 instead of 7860

**This means old build is running**:
1. Go to Settings → Factory Reboot
2. Wait for fresh build from latest GitHub commit
3. Verify logs show "Port: 7860"

### Issue: Build succeeds but health check fails

**Check**:
1. Container logs show "Uvicorn running on http://0.0.0.0:7860"
2. No Python errors in logs
3. Dependencies installed correctly

**Fix**:
- Increase health check timeout in Dockerfile
- Or disable health check temporarily

---

## Quick Checklist

Before submitting to examiner:

- [ ] GitHub repo synced to HF Space
- [ ] EMAIL configured in HF Space Settings
- [ ] SECRET configured in HF Space Settings
- [ ] PIPE_TOKEN configured (optional)
- [ ] Factory Reboot completed
- [ ] Build logs show port 7860
- [ ] Health endpoint returns HTTP 200
- [ ] Solve endpoint accepts requests
- [ ] Background processing works (check logs)

---

## Alternative: Manual Docker Deployment

If HF Space continues to fail, you can deploy manually:

### Using Docker Locally
```bash
docker build -t quiz-solver .
docker run -p 7860:7860 \
  -e EMAIL=24ds3000019@ds.study.iitm.ac.in \
  -e SECRET=banana \
  -e PIPE_TOKEN=eyJ... \
  quiz-solver
```

### Using Render.com
1. Import from GitHub
2. Set environment variables in Render dashboard
3. Use Dockerfile for deployment
4. Render will provide public URL

### Using Railway.app
1. New Project → Deploy from GitHub
2. Add environment variables
3. Automatic deployment from Dockerfile

---

## Support

If issues persist after following this guide:

1. Check build logs: https://huggingface.co/spaces/udaypratap/quiz-solver/logs
2. Verify GitHub sync: https://huggingface.co/spaces/udaypratap/quiz-solver/settings
3. Test locally: `docker build -t quiz-solver . && docker run -p 7860:7860 quiz-solver`

---

**Last Updated**: 20 November 2025, 19:00 IST
