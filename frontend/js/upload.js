// Upload Module
// Handles file upload, drag & drop, and image preview

import { showToast, toggleElement } from './ui.js';

let currentImageFile = null;

/**
 * Handle file selection from input
 * @param {Event} event - File input change event
 */
export function handleFileSelect(event) {
    const file = event.target.files[0];
    processFile(file);
}

/**
 * Handle drag and drop
 * @param {DragEvent} event - Drop event
 */
export function handleDrop(event) {
    event.preventDefault();
    
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        dropArea.classList.remove('drag-over');
    }
    
    const file = event.dataTransfer.files[0];
    processFile(file);
}

/**
 * Handle drag over
 * @param {DragEvent} event - Drag over event
 */
export function handleDragOver(event) {
    event.preventDefault();
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        dropArea.classList.add('drag-over');
    }
}

/**
 * Handle drag leave
 * @param {DragEvent} event - Drag leave event
 */
export function handleDragLeave(event) {
    const dropArea = document.getElementById('dropArea');
    if (dropArea) {
        dropArea.classList.remove('drag-over');
    }
}

/**
 * Process uploaded file
 * @param {File} file - File to process
 */
function processFile(file) {
    if (!file) {
        showToast('No file selected', 'warning');
        return;
    }
    
    if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image file', 'error');
        return;
    }
    
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('Image size must be less than 10MB', 'error');
        return;
    }
    
    currentImageFile = file;
    displayPreview(file);
    showToast('Image loaded successfully!', 'success');
}

/**
 * Display image preview
 * @param {File} file - Image file to preview
 */
function displayPreview(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const previewImage = document.getElementById('preview-image');
        if (previewImage) {
            previewImage.src = e.target.result;
        }
        
        toggleElement('preview-container', true);
        toggleElement('dropArea', false);
        toggleElement('results-placeholder', false);
        toggleElement('results-content', false);
    };
    
    reader.onerror = function() {
        showToast('Failed to read image file', 'error');
    };
    
    reader.readAsDataURL(file);
}

/**
 * Clear image preview and reset state
 */
export function clearPreview() {
    currentImageFile = null;
    
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.value = '';
    }
    
    const previewImage = document.getElementById('preview-image');
    if (previewImage) {
        previewImage.src = '';
    }
    
    toggleElement('preview-container', false);
    toggleElement('dropArea', true);
    toggleElement('results-placeholder', true);
    toggleElement('results-content', false);
}

/**
 * Set current image file (used by camera module)
 * @param {File} file - Image file to set
 */
export function setImageFile(file) {
    currentImageFile = file;
    displayPreview(file);
}

/**
 * Get current image file
 * @returns {File|null} Current image file
 */
export function getImageFile() {
    return currentImageFile;
}

/**
 * Initialize file input click handler
 */
export function initFileInput() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

export default {
    handleFileSelect,
    handleDrop,
    handleDragOver,
    handleDragLeave,
    clearPreview,
    setImageFile,
    getImageFile,
    initFileInput
};
