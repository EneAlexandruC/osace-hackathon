// Results Module
// Handles display of classification results

import { toggleElement, animateElement } from './ui.js';

/**
 * Display classification results
 * @param {Object} data - Classification data from API
 */
export function displayResults(data) {
    toggleElement('results-placeholder', false);
    toggleElement('results-content', true);
    
    // Animate results container
    animateElement('results-content', 'animate-bounce-in');
    
    // Set class with emoji
    const classEmoji = data.predicted_class.toLowerCase() === 'robot' ? '🤖' : '👤';
    const resultClass = document.getElementById('result-class');
    if (resultClass) {
        resultClass.textContent = `${classEmoji} ${data.predicted_class.toUpperCase()}`;
        resultClass.classList.add('animate-scale-in');
    }
    
    // Set confidence
    const confidence = (data.confidence * 100).toFixed(1);
    const resultConfidence = document.getElementById('result-confidence');
    if (resultConfidence) {
        resultConfidence.textContent = `${confidence}%`;
    }
    
    // Animate confidence bar
    const confidenceBar = document.getElementById('confidence-bar');
    if (confidenceBar) {
        setTimeout(() => {
            confidenceBar.style.width = `${confidence}%`;
        }, 100);
    }
    
    // Set timestamp
    const resultTimestamp = document.getElementById('result-timestamp');
    if (resultTimestamp && data.timestamp) {
        const date = new Date(data.timestamp);
        resultTimestamp.textContent = date.toLocaleString();
    }
    
    // Display probabilities
    displayProbabilities(data.all_probabilities);
}

/**
 * Display probability breakdown
 * @param {Object} probabilities - Class probabilities
 */
function displayProbabilities(probabilities) {
    const container = document.getElementById('probabilities-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.entries(probabilities).forEach(([className, probability], index) => {
        const percent = (probability * 100).toFixed(1);
        const emoji = className.toLowerCase() === 'robot' ? '🤖' : '👤';
        
        const probDiv = document.createElement('div');
        probDiv.style.animationDelay = `${index * 0.1}s`;
        probDiv.className = 'animate-slide-up';
        
        probDiv.innerHTML = `
            <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-400">${emoji} ${className}</span>
                <span class="text-white font-semibold">${percent}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                <div class="prob-bar bg-snapchat-yellow h-full rounded-full transition-all duration-1000 ease-out" 
                     style="width: 0%" 
                     data-width="${percent}"></div>
            </div>
        `;
        
        container.appendChild(probDiv);
        
        // Animate bar after adding to DOM
        setTimeout(() => {
            const bar = probDiv.querySelector('.prob-bar');
            if (bar) {
                bar.style.width = bar.dataset.width + '%';
            }
        }, 100 + (index * 100));
    });
}

/**
 * Hide results section
 */
export function hideResults() {
    toggleElement('results-placeholder', true);
    toggleElement('results-content', false);
    
    // Reset confidence bar
    const confidenceBar = document.getElementById('confidence-bar');
    if (confidenceBar) {
        confidenceBar.style.width = '0%';
    }
}

/**
 * Clear all results
 */
export function clearResults() {
    hideResults();
    
    const resultClass = document.getElementById('result-class');
    if (resultClass) resultClass.textContent = '';
    
    const resultConfidence = document.getElementById('result-confidence');
    if (resultConfidence) resultConfidence.textContent = '';
    
    const resultTimestamp = document.getElementById('result-timestamp');
    if (resultTimestamp) resultTimestamp.textContent = '';
    
    const probContainer = document.getElementById('probabilities-container');
    if (probContainer) probContainer.innerHTML = '';
}

export default {
    displayResults,
    hideResults,
    clearResults
};
