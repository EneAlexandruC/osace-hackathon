// API Service Module
// Handles all backend API communications

const API_CONFIG = {
    BASE_URL: 'https://xenia-unsmotherable-colette.ngrok-free.dev',
    ENDPOINTS: {
        PREDICT: '/api/predict',
        HISTORY: '/api/history'
    }
};

/**
 * Classify an image using the ML model
 * @param {File} imageFile - The image file to classify
 * @returns {Promise<Object>} Classification results
 */
export async function classifyImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PREDICT}`, {
        method: 'POST',
        body: formData,
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Classification failed');
    }

    return data;
}

/**
 * Fetch classification history from the backend
 * @returns {Promise<Array>} Array of classification records
 */
export async function fetchHistory() {
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HISTORY}`, {
        headers: {
            'ngrok-skip-browser-warning': 'true'
        }
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    // Backend returns 'predictions', not 'history'
    return data.predictions || data.history || [];
}

/**
 * Check if the API server is available
 * @returns {Promise<boolean>} Server availability status
 */
export async function checkServerHealth() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/`, {
            method: 'HEAD',
            timeout: 5000
        });
        return response.ok;
    } catch (error) {
        console.error('Server health check failed:', error);
        return false;
    }
}

export default {
    classifyImage,
    fetchHistory,
    checkServerHealth,
    API_CONFIG
};
