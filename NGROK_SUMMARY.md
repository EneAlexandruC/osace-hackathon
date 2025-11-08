# 🎯 Summary: ngrok Setup

## What Changed

### Before (Complicated ❌)
```
Terminal 1: python backend/app.py       (Port 5000 - API only)
Terminal 2: python -m http.server 8080  (Port 8080 - Frontend)
Terminal 3: ngrok http 5000             (ngrok tunnel)

Problems:
- Two servers to manage
- CORS issues between ports
- Absolute URLs needed
- Confusion with ports
```

### After (Simple ✅)
```
Terminal 1: python backend/app.py       (Port 5000 - API + Frontend)
Terminal 2: ngrok http 5000             (ngrok tunnel)

Benefits:
- ONE server
- NO CORS issues
- Relative URLs
- Everything just works!
```

## How It Works

```
┌─────────────────────────────────────────┐
│         ngrok Tunnel                     │
│  https://abc123.ngrok-free.dev          │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│      Flask Server (Port 5000)            │
│  ┌─────────────────────────────────┐    │
│  │  Frontend (index.html)           │    │
│  │  /  →  index.html                │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  API Endpoints                   │    │
│  │  /predict  →  Classify image     │    │
│  │  /history  →  Get history        │    │
│  │  /health   →  Health check       │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│         Supabase Database                │
│  - Store classifications                 │
│  - Store images                          │
└─────────────────────────────────────────┘
```

## The Key Change

### In `frontend/index.html`:

**Before:**
```javascript
const API_URL = 'https://xenia-unsmotherable-colette.ngrok-free.dev';
// Had to update this every time ngrok restarted!
```

**After:**
```javascript
const API_URL = '';  // Empty = relative URLs
// Works with ANY ngrok URL automatically!
```

### Why Relative URLs Work:

When frontend is at: `https://abc123.ngrok-free.dev/`  
And you request: `/predict`  
Browser goes to: `https://abc123.ngrok-free.dev/predict` ✅

Same domain = No CORS!

## Startup Commands

### Option 1: Manual (Recommended for understanding)
```powershell
# Terminal 1
python backend/app.py

# Terminal 2
ngrok http 5000
```

### Option 2: Automated Script
```powershell
# Run the startup script
.\start_ngrok.ps1
```

## Access Your App

1. Start Flask → See `Running on http://127.0.0.1:5000`
2. Start ngrok → Copy the `https://....ngrok-free.dev` URL
3. Open that URL in browser
4. Done! 🎉

## Files Modified

| File | Change | Why |
|------|--------|-----|
| `frontend/index.html` | `API_URL = ''` | Use relative URLs |
| `backend/app.py` | Already configured! | Serves static files |

## No Changes Needed To:

- ✅ Backend code
- ✅ Supabase config
- ✅ Model files
- ✅ Frontend design
- ✅ API endpoints

## Benefits

1. **Simpler** - One server instead of two
2. **Faster** - No separate frontend server needed
3. **Cleaner** - No CORS configuration needed
4. **Flexible** - Works with any ngrok URL
5. **Professional** - Industry standard approach

## Common Questions

**Q: Do I still need CORS in Flask?**  
A: Technically no (same origin), but it's there for safety and doesn't hurt.

**Q: Can I still test locally without ngrok?**  
A: Yes! Just visit `http://127.0.0.1:5000`

**Q: What if I want to use port 8080?**  
A: You can! Just change `FLASK_PORT = 8080` in `config.py` and use `ngrok http 8080`

**Q: Does this work for deployment?**  
A: Yes! Same concept for production servers (one server for everything).

## Testing Checklist

After starting Flask + ngrok:

- [ ] Visit ngrok URL
- [ ] See the frontend load
- [ ] Upload an image
- [ ] Classification works
- [ ] History loads
- [ ] Camera works
- [ ] No console errors

## Troubleshooting

### Flask won't start
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <process_id> /F
```

### ngrok shows error
- Make sure Flask is running FIRST
- Check Flask is on port 5000
- Try restarting ngrok

### Page loads but nothing works
- Check browser console (F12)
- Check Flask console for errors
- Verify Supabase credentials in `.env`

## Next Steps

1. ✅ Start your app: `python backend/app.py`
2. ✅ Start ngrok: `ngrok http 5000`
3. ✅ Share the URL with your team!
4. ✅ Use it in your hackathon presentation!

---

**Remember:** One server, one port, one ngrok tunnel. Simple! 🚀
