# Deployment FAQ & Keep-Alive Guide

## Why Does It Work Locally But Not on Render?

### Root Causes

1. **Environment Variables**
   - **Local**: Loads from `.env` file via `python-dotenv`
   - **Render**: Must come from `render.yaml` or Dashboard settings
   - **Fix**: We removed `.env.docker` dependency, now uses platform env vars

2. **Docker Build Context**
   - Render builds from fresh git clone
   - Files not committed properly won't exist in Docker build
   - `COPY` commands fail if files aren't in repository

3. **File Paths**
   - Local absolute paths differ from Docker container paths
   - Docker requires relative paths from project root

### Solutions Applied ✅

- ✅ Removed `COPY .env.docker .env` from Dockerfile
- ✅ All credentials now come from `render.yaml`
- ✅ Added proper environment variable defaults

---

## How to Keep Your Service Awake During Evaluation

### The Problem: Render Free Tier Sleep

**Render's free tier services**:
- Sleep after **15 minutes** of inactivity
- Take **30-50 seconds** to wake up on first request
- **Risk**: Examiner's first request times out ❌

### Solution 1: Built-in Keep-Alive (Automatic) ✅

Your app now has a **keep-alive mechanism**:

```python
# Pings itself every 10 minutes
ENABLE_KEEP_ALIVE=1  # Set in render.yaml
```

**How it works**:
1. Service starts up
2. After 1 minute, begins self-pinging
3. Sends GET request to `http://localhost:7860/` every 10 minutes
4. Keeps service awake during evaluation period

**Logs will show**:
```
✓ Keep-alive mechanism ENABLED (10-minute intervals)
✓ Keep-alive ping successful
```

### Solution 2: External Monitoring (Recommended for Critical Tests)

Use **UptimeRobot** (free) to ping your endpoint:

1. Go to: https://uptimerobot.com
2. Sign up (free account)
3. Create new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://quiz-solver-15k6.onrender.com/`
   - **Interval**: 5 minutes
   - **Name**: TDS Quiz Solver

**Benefits**:
- External pings from different IPs
- Email alerts if service goes down
- Works even if internal keep-alive fails

### Solution 3: Pre-warm Before Evaluation

**15 minutes before evaluation starts**:

```bash
# Run this in terminal
while true; do 
  curl https://quiz-solver-15k6.onrender.com/
  sleep 300  # Every 5 minutes
done
```

Press `Ctrl+C` to stop after evaluation ends.

---

## Verification Checklist

### Before Evaluation Starts:

- [ ] **Test endpoint is live**:
  ```bash
  curl https://quiz-solver-15k6.onrender.com/
  ```
  Should return: `{"status":"ready","service":"TDS Quiz Solver",...}`

- [ ] **Check logs for keep-alive**:
  Go to Render Dashboard → Your Service → Logs
  Look for: `✓ Keep-alive mechanism ENABLED`

- [ ] **Test solve endpoint**:
  ```bash
  curl -X POST https://quiz-solver-15k6.onrender.com/solve \
    -H "Content-Type: application/json" \
    -d '{"email":"24ds3000019@ds.study.iitm.ac.in","secret":"banana","url":"https://tds-llm-analysis.s-anand.net/demo"}'
  ```
  Should return: `{"status":"processing",...}`

- [ ] **Verify response time < 3 seconds**:
  ```bash
  time curl https://quiz-solver-15k6.onrender.com/
  ```

### During Evaluation:

1. **Keep Dashboard Open**: https://dashboard.render.com/web/srv-xxxx
2. **Monitor Logs**: Watch for incoming requests
3. **Check Keep-Alive Pings**: Should see them every 10 minutes
4. **Response Time**: Should be instant (not sleeping)

---

## Troubleshooting

### Service Still Sleeping?

**Check 1: Is keep-alive running?**
```bash
# In Render Dashboard logs, search for:
"Keep-alive mechanism ENABLED"
"Keep-alive ping successful"
```

**Check 2: Verify environment variable**
```bash
# In Render Dashboard → Environment
ENABLE_KEEP_ALIVE=1
```

**Check 3: Manual wake-up**
```bash
# Ping 3 times to ensure it's awake
curl https://quiz-solver-15k6.onrender.com/ && \
curl https://quiz-solver-15k6.onrender.com/ && \
curl https://quiz-solver-15k6.onrender.com/
```

### First Request Times Out?

**Render free tier cold start**: 30-50 seconds

**Solutions**:
1. Use UptimeRobot external monitoring
2. Pre-warm 5 minutes before evaluation
3. Run manual pings every 5 minutes during evaluation window

### Service Goes Down During Evaluation?

**Emergency fallback**:
1. Check HF Space (if you did Factory Reboot): https://udaypratap-quiz-solver.hf.space/
2. Deploy to alternative platform (Railway.app takes 8 minutes)
3. Notify examiner immediately with new URL

---

## Environment Variables Reference

### Required (Must Set)

| Variable | Value | Purpose |
|----------|-------|---------|
| `EMAIL` | `24ds3000019@ds.study.iitm.ac.in` | Authentication |
| `SECRET` | `banana` | Authentication |
| `PIPE_TOKEN` | `eyJhbGci...` | LLM API access |
| `PORT` | `7860` | Server port |

### Optional (Pre-configured)

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENABLE_KEEP_ALIVE` | `1` | Self-ping every 10min |
| `DISABLE_PLAYWRIGHT` | `0` | Enable browser automation |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |
| `RATE_LIMIT_MAX` | `10` | Max requests per window |

---

## Timeline for Your Deployment

### Current Status (as of commit a52966b):

✅ **Dockerfile fixed** - No longer tries to copy .env.docker
✅ **Keep-alive added** - Self-pings every 10 minutes  
✅ **httpx dependency** - Added for async HTTP requests
✅ **render.yaml updated** - All env vars configured
⏳ **Building on Render** - Takes 6-8 minutes

### Next Steps:

1. **Wait for build** (6-8 minutes from now)
2. **Test endpoint** when "Your service is live" appears
3. **Set up UptimeRobot** (optional but recommended)
4. **Pre-warm** 15 minutes before evaluation
5. **Submit endpoint** to examiner

### Your Submission Details:

```
Endpoint: https://quiz-solver-15k6.onrender.com/solve
Method: POST
Email: 24ds3000019@ds.study.iitm.ac.in
Secret: banana
```

---

## Why Local Works But Deployment Doesn't (Summary)

| Aspect | Local | Render Deployment |
|--------|-------|-------------------|
| **Env Vars** | `.env` file | `render.yaml` / Dashboard |
| **File Access** | Direct disk access | Docker build context only |
| **Dependencies** | Installed globally | Must be in `requirements.txt` |
| **Port** | Any port (e.g., 8000) | Must use PORT env var (7860) |
| **Sleep** | Never sleeps | Sleeps after 15min inactivity |
| **Cold Start** | Instant | 30-50 seconds first request |

**Key Takeaway**: Deployment requires everything to be:
1. ✅ Committed to git
2. ✅ Configured via environment variables
3. ✅ Listed in requirements.txt
4. ✅ Kept awake via self-ping or external monitoring

---

**Last Updated**: 20 November 2025, 20:15 IST  
**Deployment**: Render.com (Free Tier)  
**Status**: Building with keep-alive enabled ✅
