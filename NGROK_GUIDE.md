# 🚀 Simple Startup Guide with ngrok

## One Server, One Command!

Since Flask serves both the API and frontend, you only need **ONE server** on port 5000.

### Step 1: Start Flask Backend
```bash
cd D:\osace-hackathon\osace-hackathon
python backend/app.py
```

This will:
- ✅ Start Flask on port 5000
- ✅ Serve API endpoints (`/predict`, `/history`)
- ✅ Serve frontend (`/` → `index.html`)

### Step 2: Start ngrok
```bash
ngrok http 5000
```

ngrok will give you a URL like:
```
https://your-unique-id.ngrok-free.dev
```

### Step 3: Access Your App

Open in browser:
```
https://your-unique-id.ngrok-free.dev
```

**That's it!** Everything works through the same URL! 🎉

## Why This Works

### Frontend is served by Flask
```python
# In backend/app.py
app = Flask(__name__, static_folder='../frontend', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')
```

### API uses relative URLs
```javascript
// In frontend/index.html
const API_URL = '';  // Empty = same server!

// Requests go to:
// https://your-ngrok-url.ngrok-free.dev/predict
// https://your-ngrok-url.ngrok-free.dev/history
```

### No CORS issues!
Since frontend and backend are on the same domain, no CORS problems! ✨

## Complete Workflow

```bash
# 1. Start Flask (serves both frontend + API)
python backend/app.py

# 2. Start ngrok (in another terminal)
ngrok http 5000

# 3. Copy the ngrok URL and open in browser
https://abc123.ngrok-free.dev
```

## What You'll See

```
Terminal 1 (Flask):
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
✓ Database connection initialized!
✓ Keras model loaded successfully!

Terminal 2 (ngrok):
Forwarding  https://abc123.ngrok-free.dev -> http://localhost:5000
```

## Access Points

| URL | What It Does |
|-----|--------------|
| `https://your-url.ngrok-free.dev/` | Main frontend (index.html) |
| `https://your-url.ngrok-free.dev/predict` | Classification API |
| `https://your-url.ngrok-free.dev/history` | History API |
| `https://your-url.ngrok-free.dev/health` | Health check |

## Benefits

✅ **One server** - no confusion  
✅ **No CORS** - same origin  
✅ **No port conflicts** - only 5000  
✅ **Relative URLs** - works with any ngrok URL  
✅ **Easy sharing** - just share the ngrok URL  
✅ **Works anywhere** - phone, tablet, other computers  

## Troubleshooting

### Port 5000 already in use?
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Then restart Flask
python backend/app.py
```

### ngrok shows "Tunnel not found"?
- Make sure Flask is running first
- Check that Flask is on port 5000
- Restart ngrok: `ngrok http 5000`

### Page loads but API fails?
- Check Flask console for errors
- Verify model is loaded
- Check Supabase credentials in `.env`

### ngrok free tier limits?
- You get 1 ngrok tunnel at a time
- 40 connections/minute limit
- If exceeded, wait or upgrade

## Quick Test

After starting both Flask and ngrok:

1. **Visit the ngrok URL** in browser
2. **Check console** (F12) - should see welcome toast
3. **Upload an image** - should classify successfully
4. **Check history** - should load previous results

## Pro Tips

💡 **Pin your ngrok URL**: Save it so you don't have to update it  
💡 **Use ngrok dashboard**: Visit `http://localhost:4040` to see requests  
💡 **Keep terminals visible**: Easy to spot errors  
💡 **Test locally first**: Use `http://127.0.0.1:5000` before ngrok  

## Environment Variables

Make sure `.env` has:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## That's It!

No need for:
- ❌ Separate frontend server
- ❌ Port 8080
- ❌ Absolute API URLs
- ❌ CORS configuration (well, it's already there for safety)

Just:
- ✅ Start Flask on 5000
- ✅ Start ngrok
- ✅ Open the URL
- ✅ Done! 🎉

---

**Questions?**
- Flask not starting? → Check backend console
- ngrok not working? → Verify port 5000
- Frontend not loading? → Check `static_folder` in app.py
- API failing? → Check ngrok dashboard at `localhost:4040`

**Remember**: You only need ONE command: `python backend/app.py` + `ngrok http 5000`
