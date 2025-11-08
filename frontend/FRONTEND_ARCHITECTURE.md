# Frontend Modular Architecture

## 📁 Project Structure

```
frontend/
├── index_new.html          # Main HTML entry point (modular version)
├── index.html              # Original HTML file (backup)
├── css/
│   └── styles.css          # Custom styles and animations
├── js/
│   ├── main.js             # Application entry point and initialization
│   ├── api.js              # API service for backend communication
│   ├── ui.js               # UI utilities (toasts, modals, animations)
│   ├── camera.js           # Camera capture functionality
│   ├── upload.js           # File upload and drag & drop
│   ├── results.js          # Results display module
│   └── history.js          # History loading and display
└── README.md               # This file
```

## 🎨 Design System

### Colors (Snapchat Inspired)
- **Primary Yellow**: `#FFFC00` - Main accent color
- **Black**: `#000000` - Primary background
- **Gray**: `#1a1a1a` - Secondary background
- **White**: `#FFFFFF` - Text and contrast

### Animations
- **slide-up**: Elements sliding up from bottom
- **slide-down**: Elements sliding down from top
- **fade-in**: Smooth opacity transition
- **scale-in**: Elements scaling in
- **bounce-in**: Bouncy entrance animation
- **shake**: Error shake animation

## 📦 Module Overview

### 1. **main.js** - Application Entry Point
**Purpose**: Initialize app, coordinate modules, handle main workflows

**Key Functions**:
- `init()` - Initialize application on page load
- `handleClassify()` - Orchestrate image classification workflow
- `handleCameraClick()` - Open camera modal
- `handleCapturePhoto()` - Capture and process camera photo

**Dependencies**: All other modules

### 2. **api.js** - API Service Layer
**Purpose**: Centralize all backend API calls

**Key Functions**:
- `classifyImage(imageFile)` - Send image for classification
- `fetchHistory()` - Get classification history
- `checkServerHealth()` - Verify backend availability

**Configuration**:
```javascript
API_CONFIG = {
    BASE_URL: 'http://127.0.0.1:5000',
    ENDPOINTS: {
        PREDICT: '/predict',
        HISTORY: '/history'
    }
}
```

**Dependencies**: None (pure API layer)

### 3. **ui.js** - UI Utilities
**Purpose**: Manage UI state, modals, and notifications

**Key Functions**:
- `showToast(message, type)` - Display toast notifications
  - Types: `success`, `error`, `warning`, `info`
- `openModal(modalId)` - Open modal dialog
- `closeModal(modalId)` - Close modal dialog
- `showLoading(elementId)` - Show loading spinner
- `hideLoading(elementId)` - Hide loading spinner
- `toggleElement(elementId, show)` - Toggle element visibility
- `animateElement(elementId, animationClass)` - Apply animation

**Toast System**:
- Auto-dismiss after 4 seconds
- Slide-in animation from right
- Multiple types with color coding
- Stacking support

**Dependencies**: None

### 4. **camera.js** - Camera Module
**Purpose**: Handle device camera access and photo capture

**Key Functions**:
- `openCamera()` - Initialize camera stream
- `closeCamera()` - Stop camera and cleanup
- `capturePhoto()` - Capture photo from video stream
- `isCameraAvailable()` - Check camera availability

**Features**:
- Mirror effect for user-facing camera
- High-quality JPEG capture (95% quality)
- Automatic cleanup on close
- Error handling with user feedback

**Dependencies**: `ui.js`

### 5. **upload.js** - Upload Module
**Purpose**: Handle file uploads, drag & drop, and previews

**Key Functions**:
- `handleFileSelect(event)` - Process file input selection
- `handleDrop(event)` - Process drag & drop
- `handleDragOver(event)` - Visual feedback during drag
- `handleDragLeave(event)` - Remove drag feedback
- `clearPreview()` - Reset upload state
- `setImageFile(file)` - Set current image (used by camera)
- `getImageFile()` - Get current image

**Features**:
- Drag & drop with visual feedback
- Image validation (type, size < 10MB)
- Automatic preview generation
- FileReader API for client-side preview

**Dependencies**: `ui.js`

### 6. **results.js** - Results Module
**Purpose**: Display classification results with animations

**Key Functions**:
- `displayResults(data)` - Show classification results
- `hideResults()` - Hide results section
- `clearResults()` - Reset results display

**Features**:
- Animated confidence bars
- Emoji-based class indicators (🤖/👤)
- Probability breakdown visualization
- Staggered animations for smooth transitions

**Dependencies**: `ui.js`

### 7. **history.js** - History Module
**Purpose**: Load and display classification history

**Key Functions**:
- `loadHistory()` - Fetch and display history
- `refreshHistory()` - Reload history
- `closeImageViewer()` - Close image modal

**Features**:
- Grid layout with responsive cards
- Click to view full-size image
- Staggered card animations
- Fallback image for missing images
- Displays up to 12 most recent items

**Dependencies**: `api.js`, `ui.js`

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                        User Action                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  main.js (Orchestrator)                  │
│  - Coordinates between modules                           │
│  - Handles main workflows                                │
└─────────────────────────────────────────────────────────┘
                            ↓
         ┌──────────────────┴──────────────────┐
         ↓                                      ↓
┌──────────────────┐                  ┌──────────────────┐
│   upload.js /    │                  │     api.js       │
│   camera.js      │                  │  - API calls     │
│  - Get image     │    ────────→     │  - Data fetch    │
└──────────────────┘                  └──────────────────┘
                                               ↓
                                      ┌──────────────────┐
                                      │   Backend API    │
                                      │   (Flask)        │
                                      └──────────────────┘
                                               ↓
         ┌─────────────────────────────────────┘
         ↓                                      ↓
┌──────────────────┐                  ┌──────────────────┐
│   results.js     │                  │   history.js     │
│  - Display       │                  │  - Display       │
│    results       │                  │    history       │
└──────────────────┘                  └──────────────────┘
         ↓                                      ↓
┌─────────────────────────────────────────────────────────┐
│                    ui.js (UI Layer)                      │
│  - Toasts, modals, animations                            │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Usage

### Starting the Application

1. **Using the modular version**:
   ```bash
   # Serve with Python
   cd frontend
   python -m http.server 8080
   
   # Or use any static file server
   # Access at http://localhost:8080/index_new.html
   ```

2. **Important**: Use `index_new.html` for the modular version

### Adding New Features

#### Adding a New Module

1. Create `js/newmodule.js`
2. Export functions:
   ```javascript
   export function myFunction() {
       // Implementation
   }
   
   export default { myFunction };
   ```

3. Import in `main.js`:
   ```javascript
   import { myFunction } from './newmodule.js';
   ```

#### Adding a New Toast Type

In `ui.js`:
```javascript
const TOAST_CONFIG = {
    icons: {
        // ... existing types
        custom: '🎉'
    },
    colors: {
        // ... existing types
        custom: 'bg-purple-500'
    }
};
```

#### Adding a New API Endpoint

In `api.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'http://127.0.0.1:5000',
    ENDPOINTS: {
        // ... existing endpoints
        NEW_ENDPOINT: '/new-route'
    }
};

export async function newApiCall() {
    const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.NEW_ENDPOINT}`
    );
    return await response.json();
}
```

## 🎯 Benefits of Modular Architecture

### ✅ Separation of Concerns
- Each module has a single responsibility
- Easy to locate and fix bugs
- Changes are isolated to specific modules

### ✅ Maintainability
- Clean, organized codebase
- Easy to understand module purposes
- Self-documenting code structure

### ✅ Reusability
- Modules can be reused across projects
- Functions are exportable and composable
- DRY (Don't Repeat Yourself) principle

### ✅ Testability
- Each module can be tested independently
- Mock dependencies easily
- Unit tests per module

### ✅ Scalability
- Easy to add new features
- Minimal code coupling
- Can grow without becoming unwieldy

### ✅ Team Collaboration
- Multiple developers can work on different modules
- Clear module boundaries
- Reduced merge conflicts

## 🔧 Development Guidelines

### Code Style
- Use ES6+ features (arrow functions, const/let, template literals)
- Async/await for asynchronous operations
- JSDoc comments for functions
- Descriptive variable and function names

### Error Handling
- Always wrap API calls in try-catch
- Show user-friendly error messages via toasts
- Log errors to console for debugging
- Graceful degradation

### Performance
- Lazy load modules when possible
- Debounce expensive operations
- Use CSS animations over JavaScript when possible
- Optimize image sizes before upload

### Accessibility
- Keyboard shortcuts (ESC to close modals)
- Semantic HTML elements
- ARIA labels where needed
- Focus management in modals

## 📝 TODO / Future Enhancements

- [ ] Add TypeScript for type safety
- [ ] Implement state management (Redux/Zustand)
- [ ] Add unit tests (Jest)
- [ ] Add E2E tests (Playwright)
- [ ] Implement service worker for offline support
- [ ] Add image cropping before classification
- [ ] Implement batch upload
- [ ] Add export history feature
- [ ] Dark/light theme toggle (currently fixed dark)
- [ ] Internationalization (i18n)

## 🐛 Troubleshooting

### Module Import Errors
**Problem**: `Uncaught SyntaxError: Cannot use import statement outside a module`

**Solution**: Ensure script tag has `type="module"`:
```html
<script type="module" src="js/main.js"></script>
```

### CORS Errors
**Problem**: `Access to fetch blocked by CORS policy`

**Solution**: Ensure Flask backend has CORS enabled:
```python
from flask_cors import CORS
CORS(app)
```

### Camera Not Working
**Problem**: Camera doesn't start

**Checklist**:
- Use HTTPS or localhost (camera requires secure context)
- Grant camera permissions in browser
- Check browser console for errors
- Ensure camera is not in use by another app

### Toast Notifications Not Showing
**Problem**: Toasts don't appear

**Checklist**:
- Verify `<div id="toast-container">` exists in HTML
- Check browser console for errors
- Ensure `ui.js` is loaded before calling `showToast()`

## 📚 Dependencies

### External Libraries
- **Tailwind CSS** (v3.x) - Utility-first CSS framework
- **HTMX** (v1.9.10) - HTML-driven interactivity (currently minimal usage)

### Browser APIs Used
- **Fetch API** - HTTP requests
- **MediaDevices API** - Camera access
- **FileReader API** - Image preview
- **Canvas API** - Photo capture

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

Same as parent project

## 👥 Contributing

When contributing to the frontend:

1. Create module in appropriate `js/` file
2. Export functions using ES6 exports
3. Import in `main.js` or dependent module
4. Add JSDoc comments
5. Update this README with new module info
6. Test across browsers
7. Check console for errors

---

**Version**: 2.0 (Modular)  
**Last Updated**: November 8, 2025  
**Maintainer**: Development Team
