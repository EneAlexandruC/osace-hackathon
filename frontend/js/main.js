// Main Application Module
// Entry point that initializes all modules and handles classification

import { classifyImage } from './api.js';
import { showToast, showLoading, hideLoading, toggleElement, initModalKeyboardShortcuts, TOAST_TYPES } from './ui.js';
import { openCamera, closeCamera, capturePhoto } from './camera.js';
import { handleDrop, handleDragOver, handleDragLeave, clearPreview, setImageFile, getImageFile, initFileInput } from './upload.js';
import { displayResults, hideResults } from './results.js';
import { loadHistory, refreshHistory, closeImageViewer } from './history.js';

/**
 * Initialize the application
 */
function init() {
    console.log('🚀 AI Classifier initializing...');
    
    // Initialize keyboard shortcuts
    initModalKeyboardShortcuts();
    
    // Initialize file input
    initFileInput();
    
    // Load initial history
    loadHistory();
    
    // Show welcome toast
    showToast('Welcome to AI Classifier! 🚀', TOAST_TYPES.INFO);
    
    console.log('✅ AI Classifier initialized successfully');
}

/**
 * Handle camera button click
 */
async function handleCameraClick() {
    await openCamera();
}

/**
 * Handle camera photo capture
 */
async function handleCapturePhoto() {
    try {
        const photoFile = await capturePhoto();
        setImageFile(photoFile);
        closeCamera();
    } catch (error) {
        showToast('Failed to capture photo', TOAST_TYPES.ERROR);
        console.error('Capture error:', error);
    }
}

/**
 * Handle file upload button click
 */
function handleFileUploadClick() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.click();
    }
}

/**
 * Handle image classification
 */
async function handleClassify() {
    const imageFile = getImageFile();
    
    if (!imageFile) {
        showToast('Please select an image first', TOAST_TYPES.WARNING);
        return;
    }
    
    // Show loading state
    toggleElement('classify-btn', false);
    showLoading('loading-state');
    hideResults();
    
    try {
        const data = await classifyImage(imageFile);
        displayResults(data);
        showToast(`Classified as ${data.predicted_class}!`, TOAST_TYPES.SUCCESS);
        
        // Refresh history after successful classification
        setTimeout(() => loadHistory(), 500);
        
    } catch (error) {
        showToast('Classification failed: ' + error.message, TOAST_TYPES.ERROR);
        console.error('Classification error:', error);
    } finally {
        toggleElement('classify-btn', true);
        hideLoading('loading-state');
    }
}

/**
 * Handle drop area click
 */
function handleDropAreaClick() {
    handleFileUploadClick();
}

// Attach functions to window object for HTML onclick handlers
window.openCameraModal = handleCameraClick;
window.closeCameraModal = closeCamera;
window.capturePhoto = handleCapturePhoto;
window.handleFileUploadClick = handleFileUploadClick;
window.handleDrop = handleDrop;
window.handleDragOver = handleDragOver;
window.handleDragLeave = handleDragLeave;
window.clearPreview = clearPreview;
window.classifyImage = handleClassify;
window.loadHistory = refreshHistory;
window.closeImageModal = closeImageViewer;
window.handleDropAreaClick = handleDropAreaClick;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

export default {
    init,
    handleCameraClick,
    handleCapturePhoto,
    handleFileUploadClick,
    handleClassify,
    handleDropAreaClick
};
