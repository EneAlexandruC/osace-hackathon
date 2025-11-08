// UI Module
// Handles toast notifications, modals, and UI state management

const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

const TOAST_CONFIG = {
    icons: {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    },
    colors: {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    },
    duration: 4000
};

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type (success, error, warning, info)
 */
export function showToast(message, type = TOAST_TYPES.INFO) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        console.error('Toast container not found');
        return;
    }

    const toast = document.createElement('div');
    const icon = TOAST_CONFIG.icons[type];
    const color = TOAST_CONFIG.colors[type];
    
    toast.className = `${color} text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 animate-slide-down transform transition-all duration-300`;
    toast.innerHTML = `
        <span class="text-2xl">${icon}</span>
        <span class="font-semibold">${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, TOAST_CONFIG.duration);
}

/**
 * Show loading state
 * @param {string} elementId - ID of the element to show loading in
 */
export function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('hidden');
    }
}

/**
 * Hide loading state
 * @param {string} elementId - ID of the element to hide loading from
 */
export function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

/**
 * Toggle element visibility
 * @param {string} elementId - ID of the element to toggle
 * @param {boolean} show - Whether to show or hide
 */
export function toggleElement(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        if (show) {
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    }
}

/**
 * Open a modal
 * @param {string} modalId - ID of the modal to open
 */
export function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Close a modal
 * @param {string} modalId - ID of the modal to close
 */
export function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

/**
 * Add escape key listener for modals
 */
export function initModalKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Close all modals
            document.querySelectorAll('[id$="-modal"]').forEach(modal => {
                modal.classList.add('hidden');
            });
            document.body.style.overflow = 'auto';
        }
    });
}

/**
 * Animate element with specified animation class
 * @param {string} elementId - ID of the element to animate
 * @param {string} animationClass - Tailwind animation class
 */
export function animateElement(elementId, animationClass) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add(animationClass);
        element.addEventListener('animationend', () => {
            element.classList.remove(animationClass);
        }, { once: true });
    }
}

export default {
    showToast,
    showLoading,
    hideLoading,
    toggleElement,
    openModal,
    closeModal,
    initModalKeyboardShortcuts,
    animateElement,
    TOAST_TYPES
};
