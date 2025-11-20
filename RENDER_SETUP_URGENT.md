# 🚨 URGENT: Render.com Environment Variables Setup

## Problem
Render is NOT loading environment variables from render.yaml. You must add them manually in the dashboard.

## Immediate Fix (5 minutes)

### Step 1: Go to Your Service Dashboard
Open: https://dashboard.render.com

Find your service: **tds-quiz-solver** (or quiz-solver-15k6)

Click on it.

### Step 2: Add Environment Variables

Click **"Environment"** tab on the left sidebar.

Click **"Add Environment Variable"** button.

Add these **EXACTLY** (copy-paste to avoid typos):

#### Variable 1: EMAIL
```
Key: EMAIL
Value: 24ds3000019@ds.study.iitm.ac.in
```

#### Variable 2: SECRET
```
Key: SECRET
Value: banana
```

#### Variable 3: PIPE_TOKEN
```
Key: PIPE_TOKEN
Value: eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDE5QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.e-weorC0bDwFYratH3hrojc7XV5C-a0n82jWpn743rE
```
**IMPORTANT**: Mark this as **"Secret"** (toggle the lock icon) so it's hidden in logs.

#### Variable 4: PORT
```
Key: PORT
Value: 7860
```

#### Variable 5: ENABLE_KEEP_ALIVE
```
Key: ENABLE_KEEP_ALIVE
Value: 1
```

#### Variable 6: DISABLE_PLAYWRIGHT
```
Key: DISABLE_PLAYWRIGHT
Value: 0
```

### Step 3: Save and Redeploy

1. Click **"Save Changes"** button (bottom right)
2. Render will automatically redeploy (takes 2-3 minutes)
3. Watch the logs for success

### Step 4: Verify Success

Look for these in the logs (after redeploy):

```
✅ Email configured: 24ds3000019@ds.study.iitm.ac.in
✅ PIPE_TOKEN: Configured
✅ Playwright Chromium: Ready
✅ Keep-alive mechanism ENABLED
Port: 7860
```

**NOT**:
```
⚠️  WARNING: EMAIL not set  ❌ (means still broken)
⚠️  WARNING: SECRET not set  ❌ (means still broken)
Port: 10000  ❌ (should be 7860)
```

### Step 5: Test Endpoint

Once logs show success:

```bash
curl https://quiz-solver-15k6.onrender.com/
```

Should return:
```json
{
  "status": "ready",
  "service": "TDS Quiz Solver",
  "version": "1.0.0",
  "playwright_enabled": true
}
```

---

## Why render.yaml Didn't Work

Render.com has a quirk: **Environment variables in render.yaml are ONLY applied during initial service creation**, not on updates.

Since your service was created before we updated render.yaml with all the env vars, they weren't applied.

**Manual dashboard entry is the ONLY way to update them now.**

---

## Alternative: Delete and Recreate Service

If you prefer a clean slate:

### Option A: Use render.yaml (Recreate Service)

1. **Delete current service**:
   - Dashboard → Your Service → Settings → Delete Service
   
2. **Create new service**:
   - Dashboard → New → Web Service
   - Connect GitHub repo: udayprattap/quiz-solver
   - Render will auto-detect render.yaml
   - Add PIPE_TOKEN manually as secret
   - Deploy

3. **Get new URL** (will be different)

### Option B: Keep Current Service (Recommended)

Just add env vars manually (faster, keeps same URL).

---

## Summary

**Root Cause**: render.yaml env vars only apply at service creation time, not updates.

**Fix**: Add all 6 environment variables manually in Render Dashboard → Environment tab.

**Time**: 5 minutes

**After**: Service will start successfully and be ready for evaluation.

---

**Created**: 20 November 2025, 20:50 IST
**Urgency**: HIGH - Required for deployment to work
