// Camera Module
// Handles camera capture functionality

import { showToast, openModal, closeModal } from './ui.js';

let cameraStream = null;

/**
 * Open camera modal and start video stream
 */
export async function openCamera() {
    openModal('camera-modal');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        
        cameraStream = stream;
        const videoElement = document.getElementById('camera-preview');
        if (videoElement) {
            videoElement.srcObject = stream;
        }
        
        showToast('Camera activated!', 'success');
    } catch (error) {
        showToast('Failed to access camera', 'error');
        console.error('Camera error:', error);
        closeCamera();
    }
}

/**
 * Close camera modal and stop video stream
 */
export function closeCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    const videoElement = document.getElementById('camera-preview');
    if (videoElement) {
        videoElement.srcObject = null;
    }
    
    closeModal('camera-modal');
}

/**
 * Capture photo from camera
 * @returns {Promise<File>} Captured image as File object
 */
export function capturePhoto() {
    return new Promise((resolve, reject) => {
        const video = document.getElementById('camera-preview');
        const canvas = document.getElementById('camera-canvas');
        
        if (!video || !canvas) {
            reject(new Error('Camera elements not found'));
            return;
        }
        
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Flip horizontally for mirror effect
        context.scale(-1, 1);
        context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
        
        canvas.toBlob(blob => {
            if (blob) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const file = new File([blob], `camera_${timestamp}.jpg`, { type: 'image/jpeg' });
                resolve(file);
                showToast('Photo captured!', 'success');
            } else {
                reject(new Error('Failed to capture photo'));
            }
        }, 'image/jpeg', 0.95);
    });
}

/**
 * Check if camera is available
 * @returns {Promise<boolean>} Camera availability
 */
export async function isCameraAvailable() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.some(device => device.kind === 'videoinput');
    } catch (error) {
        console.error('Error checking camera availability:', error);
        return false;
    }
}

export default {
    openCamera,
    closeCamera,
    capturePhoto,
    isCameraAvailable
};
