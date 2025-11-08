# Troubleshooting Guide - Modal & History Issues

## Issues Fixed

### 1. **CORS & ngrok Headers**
- Added `ngrok-skip-browser-warning` header to all API requests
- Updated backend CORS configuration for ngrok compatibility
- Added `@app.after_request` handler for proper headers

### 2. **ES6 Module Loading Issues**
- Created `index_simple.html` - single-file version without modules
- All JavaScript is inline, no import/export issues
- Works with any file server (no module CORS restrictions)

### 3. **History Not Showing**
- Fixed hidden state management
- Ensured proper classList toggle
- Added proper error handling with console logs

## Files Created/Updated

### ✅ Updated Files

1. **backend/app.py**
   - Added comprehensive CORS configuration
   - Added ngrok-specific headers
   - Added `@app.after_request` decorator

2. **frontend/js/api.js**
   - Added `ngrok-skip-browser-warning` header to all requests
   - For modular version users

3. **frontend/index_simple.html** (NEW - RECOMMENDED)
   - Single-file implementation
   - No module loading issues
   - All JavaScript inline
   - Works immediately

## Quick Fix Solutions

### Solution 1: Use Simple Version (RECOMMENDED)

```bash
# Just open this file in your browser:
http://localhost:8080/index_simple.html
```

**Why this works:**
- No ES6 modules = no CORS issues
- Inline JavaScript = no file loading problems
- Direct access to all functions
- Simpler debugging

### Solution 2: Restart Backend with New Config

```bash
# Stop current backend (Ctrl+C)
python backend/app.py
```

The new CORS configuration will:
- Allow ngrok requests
- Add proper headers
- Skip browser warnings

### Solution 3: Check Browser Console

Open Developer Tools (F12) and check for:

**Common Errors:**
```
❌ CORS policy blocked
   Fix: Restart backend with new app.py

❌ Failed to load module
   Fix: Use index_simple.html instead

❌ ngrok browser warning
   Fix: Already fixed in new code

❌ History shows as empty
   Fix: Check API_URL in HTML matches your ngrok URL
```

### Solution 4: Update API URL

In `index_simple.html` line 318:
```javascript
const API_URL = 'https://your-ngrok-url-here.ngrok-free.dev';
```

Make sure this matches your actual ngrok URL!

## Testing Checklist

### ✅ Before Testing

- [ ] Backend is running (`python backend/app.py`)
- [ ] Frontend server is running (`python -m http.server 8080` in frontend folder)
- [ ] ngrok is running (if using remote access)
- [ ] API_URL in HTML matches your backend URL

### ✅ Test Each Feature

1. **Upload Image**
   - [ ] Click "Upload File" button
   - [ ] File input dialog opens
   - [ ] Image preview shows
   - [ ] No console errors

2. **Camera Capture**
   - [ ] Click "Use Camera" button
   - [ ] Camera modal appears
   - [ ] Video stream shows
   - [ ] Can capture photo
   - [ ] Modal closes properly

3. **Classification**
   - [ ] Click "Classify Image" button
   - [ ] Loading spinner shows
   - [ ] Results appear
   - [ ] Confidence bar animates
   - [ ] Toast notification shows

4. **History**
   - [ ] History section loads on page load
   - [ ] Cards appear if data exists
   - [ ] Placeholder shows if empty
   - [ ] Can click to view full image
   - [ ] Refresh button works

5. **Modals**
   - [ ] Camera modal opens/closes
   - [ ] Image viewer modal opens/closes
   - [ ] ESC key closes modals
   - [ ] Click outside closes modals

## Debugging Steps

### Step 1: Check Network Tab

1. Open Developer Tools (F12)
2. Go to Network tab
3. Try loading history
4. Check the request to `/history`

**What to look for:**
- ✅ Status 200 = Success
- ❌ Status 403 = CORS issue (restart backend)
- ❌ Status 404 = Wrong URL (check API_URL)
- ❌ Status 500 = Backend error (check backend console)

### Step 2: Check Console

Look for these messages:

**Good:**
```
✓ Database connection initialized!
✓ Keras model loaded successfully!
🚀 AI Classifier initializing...
```

**Bad:**
```
❌ Failed to load module
❌ CORS policy blocked
❌ TypeError: Cannot read property...
```

### Step 3: Test API Directly

Open browser and visit:
```
https://your-ngrok-url.ngrok-free.dev/history
```

**Expected:** JSON response with history data
**If error:** Backend is not running or CORS issue

### Step 4: Check Element IDs

Open Console and run:
```javascript
console.log('Toast:', document.getElementById('toast-container'));
console.log('History:', document.getElementById('history-container'));
console.log('Modal:', document.getElementById('camera-modal'));
```

All should return elements, not `null`.

## Common Issues & Fixes

### Issue: "Nothing happens when I click buttons"

**Diagnosis:**
- Check Console for JavaScript errors
- Check if functions are defined

**Fix:**
```javascript
// In Console, test:
typeof openCameraModal  // Should be "function"
typeof loadHistory      // Should be "function"
```

If "undefined", the script didn't load properly.

### Issue: "History shows 'No classifications yet' but I have data"

**Diagnosis:**
- API request failing
- Wrong URL
- CORS blocking

**Fix:**
1. Check Network tab for `/history` request
2. Verify API_URL matches your backend
3. Check response data structure
4. Restart backend with new CORS config

### Issue: "Camera modal doesn't open"

**Diagnosis:**
- JavaScript error
- Modal element not found
- classList not working

**Fix:**
```javascript
// Test in Console:
document.getElementById('camera-modal').classList.remove('hidden');
```

Should make modal visible.

### Issue: "Images in history don't load"

**Diagnosis:**
- Wrong Supabase URL
- RLS policies blocking
- Image file doesn't exist

**Fix:**
1. Check `image_url` in response
2. Try opening URL directly in browser
3. Check Supabase Storage permissions
4. Run `fix_storage_policies.sql` if needed

## File Comparison

### Use `index_simple.html` if:
- ✅ You want it to work immediately
- ✅ You don't need modular code
- ✅ You're having module loading issues
- ✅ Easier debugging

### Use `index_new.html` (modular) if:
- ✅ You want clean, organized code
- ✅ You plan to expand features
- ✅ You're comfortable with ES6 modules
- ✅ You need separate files for team work

## Still Not Working?

### Nuclear Option: Fresh Start

1. **Stop all servers:**
   ```bash
   # Ctrl+C on all terminal windows
   ```

2. **Clear browser cache:**
   - Press Ctrl+Shift+Delete
   - Clear cached images and files
   - Clear cookies

3. **Restart everything:**
   ```bash
   # Terminal 1: Backend
   cd D:\osace-hackathon\osace-hackathon
   python backend/app.py
   
   # Terminal 2: Frontend
   cd D:\osace-hackathon\osace-hackathon\frontend
   python -m http.server 8080
   
   # Terminal 3: ngrok (if using)
   ngrok http 5000
   ```

4. **Update API_URL:**
   - Open `frontend/index_simple.html`
   - Line 318: Update to your ngrok URL or `http://127.0.0.1:5000`

5. **Open in browser:**
   ```
   http://localhost:8080/index_simple.html
   ```

6. **Open Developer Tools (F12)**
   - Check Console for errors
   - Check Network for failed requests

## Success Indicators

You'll know it's working when:

1. ✅ Page loads with Snapchat yellow/black theme
2. ✅ Console shows "Welcome to AI Classifier! 🚀" toast
3. ✅ History section shows either cards or "No classifications yet"
4. ✅ Clicking "Use Camera" opens modal
5. ✅ Network tab shows successful `/history` request
6. ✅ No red errors in Console

## Contact Points

If still having issues, check:

1. **Backend Console** - Python errors, model loading
2. **Browser Console** - JavaScript errors, API errors
3. **Network Tab** - Request/response status
4. **Supabase Dashboard** - Database records, storage files

## Quick Reference

### File Locations
```
frontend/
├── index_simple.html    ← USE THIS (single file, no modules)
├── index_new.html       ← Modular version
├── index.html           ← Original (backup)
└── js/
    ├── main.js
    ├── api.js           ← Updated with ngrok headers
    ├── ui.js
    ├── camera.js
    ├── upload.js
    ├── results.js
    └── history.js

backend/
└── app.py               ← Updated with CORS config
```

### Key Configuration
```javascript
// In index_simple.html (line 318)
const API_URL = 'https://your-url.ngrok-free.dev';

// In backend/config.py
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
```

---

**Last Updated:** November 8, 2025  
**Status:** All fixes implemented  
**Recommended:** Use `index_simple.html` for immediate results
