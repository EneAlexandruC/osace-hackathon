// History Module
// Handles loading and displaying classification history

import { fetchHistory } from './api.js';
import { showToast, toggleElement, openModal } from './ui.js';

/**
 * Load and display classification history
 */
export async function loadHistory() {
    try {
        const history = await fetchHistory();
        displayHistory(history);
    } catch (error) {
        showToast('Failed to load history', 'error');
        console.error('Error loading history:', error);
    }
}

/**
 * Display history items
 * @param {Array} history - Array of classification records
 */
function displayHistory(history) {
    const container = document.getElementById('history-container');
    const placeholder = document.getElementById('history-placeholder');
    
    if (!container || !placeholder) return;
    
    if (history && history.length > 0) {
        placeholder.classList.add('hidden');
        container.classList.remove('hidden');
        container.innerHTML = '';
        
        // Display up to 12 most recent items
        history.slice(0, 12).forEach((item, index) => {
            const card = createHistoryCard(item, index);
            container.appendChild(card);
        });
    } else {
        placeholder.classList.remove('hidden');
        container.classList.add('hidden');
        container.innerHTML = '';
    }
}

/**
 * Create a history card element
 * @param {Object} item - History item data
 * @param {number} index - Item index for staggered animation
 * @returns {HTMLElement} History card element
 */
function createHistoryCard(item, index) {
    const classEmoji = item.predicted_class.toLowerCase() === 'robot' ? '🤖' : '👤';
    const confidence = (item.confidence * 100).toFixed(1);
    const date = new Date(item.created_at);
    
    const card = document.createElement('div');
    card.style.animationDelay = `${index * 0.05}s`;
    card.className = 'bg-snapchat-gray rounded-2xl overflow-hidden hover:scale-105 transition-all duration-300 cursor-pointer glow-hover animate-scale-in card-hover';
    card.onclick = () => openImageViewer(item.image_url);
    
    card.innerHTML = `
        <div class="relative overflow-hidden">
            <img src="${item.image_url}" 
                 alt="${item.predicted_class}" 
                 class="w-full h-48 object-cover hover:scale-110 transition-transform duration-300"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27400%27 height=%27300%27%3E%3Crect fill=%27%231a1a1a%27 width=%27400%27 height=%27300%27/%3E%3Ctext fill=%27%23666%27 font-family=%27Arial%27 font-size=%2720%27 x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27 dy=%27.3em%27%3EImage not found%3C/text%3E%3C/svg%3E'">
            <div class="absolute top-2 right-2 bg-snapchat-yellow text-black px-3 py-1 rounded-full font-bold text-sm">
                ${confidence}%
            </div>
        </div>
        <div class="p-4">
            <div class="flex items-center justify-between mb-2">
                <span class="text-2xl">${classEmoji}</span>
                <span class="text-snapchat-yellow font-bold text-lg uppercase">${item.predicted_class}</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-1 mt-2 mb-3">
                <div class="bg-snapchat-yellow h-full rounded-full transition-all duration-500" 
                     style="width: ${confidence}%"></div>
            </div>
            <div class="flex items-center gap-2 text-xs text-gray-500">
                <span>⏱️</span>
                <span>${date.toLocaleDateString()} ${date.toLocaleTimeString()}</span>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * Open image viewer modal with full-size image
 * @param {string} imageUrl - URL of the image to display
 */
function openImageViewer(imageUrl) {
    const modalImage = document.getElementById('modal-image');
    if (modalImage) {
        modalImage.src = imageUrl;
    }
    openModal('image-modal');
}

/**
 * Close image viewer modal
 */
export function closeImageViewer() {
    const modal = document.getElementById('image-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

/**
 * Refresh history display
 */
export async function refreshHistory() {
    showToast('Refreshing history...', 'info');
    await loadHistory();
}

export default {
    loadHistory,
    refreshHistory,
    closeImageViewer
};
