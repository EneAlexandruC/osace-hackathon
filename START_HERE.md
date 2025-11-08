# ⚡ Ultra-Simple Startup

## Two Terminal Windows. Two Commands. Done.

### Terminal 1: Start Flask
```bash
python backend/app.py
```

Wait until you see:
```
✓ Database connection initialized!
✓ Keras model loaded successfully!
 * Running on http://127.0.0.1:5000
```

### Terminal 2: Start ngrok
```bash
ngrok http 5000
```

You'll see something like:
```
Forwarding    https://abc-123-xyz.ngrok-free.dev -> http://localhost:5000
```

### Open in Browser

Copy the `https://....ngrok-free.dev` URL and open it in your browser!

**That's it!** 🎉

---

## Why No Port 8080?

Because Flask serves everything:
- **Frontend** (HTML, CSS, JS) from `/`
- **API** (`/predict`, `/history`) from same server

One server = No CORS problems! ✨

## The Magic

Your `index.html` now uses:
```javascript
const API_URL = '';  // Empty string = relative URLs
```

So requests go to:
- `https://your-ngrok-url/predict` ✅
- `https://your-ngrok-url/history` ✅

All on the same domain! No cross-origin issues!

---

**Stop Everything**: Just press `Ctrl+C` in both terminals
