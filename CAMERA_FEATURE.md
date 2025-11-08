# Camera Feature Documentation

## Overview
Users can now choose between using their device camera or uploading an image from their files.

## Features

### 1. Upload Options
When opening the application, users see two buttons:
- **📷 Folosește Camera** - Opens device camera
- **📁 Alege din Fișiere** - Opens file browser

### 2. Camera Capture
- Opens device camera in a modal window
- Shows live video preview
- Capture button (📸) takes a photo
- Close button (✖) cancels and closes camera
- Press ESC key to close camera modal

### 3. File Upload
- Traditional file browser
- Supports drag & drop
- Accepts: PNG, JPG, JPEG, GIF, BMP (max 16MB)

## Technical Details

### Camera API
Uses the **MediaDevices.getUserMedia()** Web API:
```javascript
navigator.mediaDevices.getUserMedia({ 
    video: { facingMode: 'environment' } 
});
```

### Browser Compatibility
- ✅ Chrome 53+
- ✅ Firefox 36+
- ✅ Safari 11+
- ✅ Edge 12+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Security Requirements
- **HTTPS Required**: Camera access only works on HTTPS or localhost
- **User Permission**: Browser will ask for camera permission
- **Privacy**: Camera stops immediately after capture

### Image Processing
1. Camera stream displayed in `<video>` element
2. Capture draws video frame to `<canvas>`
3. Canvas converted to JPEG blob
4. Blob converted to File object
5. File sent to prediction API

## Mobile Optimization

### Responsive Design
- Single column layout on mobile
- Larger touch targets for buttons
- Full-width camera preview
- Stack camera controls vertically

### Mobile Camera
- **facingMode: 'environment'** - Uses back camera on mobile
- Auto-rotation support
- Touch-friendly controls

## User Flow

### Camera Flow
```
1. Click "Folosește Camera" button
2. Grant camera permission (first time)
3. See live camera preview
4. Click "Capturează Fotografia"
5. Image preview shown
6. Click "Analizează Imaginea"
7. Results displayed
```

### File Upload Flow
```
1. Click "Alege din Fișiere" button
2. Select image from device
   OR drag & drop image
3. Image preview shown
4. Click "Analizează Imaginea"
5. Results displayed
```

## Error Handling

### Camera Errors
- **Permission Denied**: Alert shown if user denies camera access
- **No Camera**: Alert if device has no camera
- **Camera In Use**: Alert if camera is being used by another app

### Fallback
If camera fails, users can always use file upload option.

## Keyboard Shortcuts
- **ESC** - Close camera modal
- **ESC** - Close image details modal

## Code Structure

### HTML Elements
```html
<!-- Upload Options -->
<div class="upload-options">
  <button id="cameraBtn">📷 Folosește Camera</button>
  <button id="fileBtn">📁 Alege din Fișiere</button>
</div>

<!-- Camera Modal -->
<div id="cameraModal">
  <video id="cameraVideo"></video>
  <canvas id="cameraCanvas"></canvas>
  <button id="captureBtn">📸 Capturează</button>
  <button id="closeCameraBtn">✖ Închide</button>
</div>
```

### Key Functions
- `openCamera()` - Request camera access and display stream
- `closeCamera()` - Stop camera and close modal
- `captureBtn.click` - Capture photo from video stream
- Canvas API for image capture

## Best Practices

### For Users
1. Allow camera permission when prompted
2. Ensure good lighting for better predictions
3. Hold device steady when capturing
4. Close camera when done to save battery

### For Developers
1. Always stop camera stream when closing
2. Handle permission errors gracefully
3. Test on multiple devices/browsers
4. Optimize canvas size for performance

## Future Enhancements
- [ ] Front/back camera toggle
- [ ] Photo filters/effects
- [ ] Multiple photo capture
- [ ] Video recording support
- [ ] QR code scanning
