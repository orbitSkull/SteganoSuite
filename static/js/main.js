/**
 * SteganoSuite - Main JavaScript File
 * Handles drag-and-drop, tab switching, form interactions, and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile navigation
    initMobileNav();
    
    // Initialize drop zones
    initDropZones();
    
    // Initialize flash message auto-dismiss
    initFlashMessages();
});

/**
 * Mobile Navigation Toggle
 */
function initMobileNav() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            const icon = navToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }
}

/**
 * Tab Switching
 */
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedContent = document.getElementById(tabName + '-tab');
    if (selectedContent) {
        selectedContent.classList.add('active');
    }
    
    // Add active class to clicked button
    const clickedButton = event.target.closest('.tab-btn');
    if (clickedButton) {
        clickedButton.classList.add('active');
    }
}

/**
 * Drop Zone Initialization
 */
function initDropZones() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(zone => {
        const input = zone.querySelector('input[type="file"]');
        const preview = zone.querySelector('.drop-zone-preview');
        const content = zone.querySelector('.drop-zone-content');
        
        if (!input) return;
        
        // Drag enter
        zone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        // Drag over
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        // Drag leave
        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            if (!zone.contains(e.relatedTarget)) {
                zone.classList.remove('drag-over');
            }
        });
        
        // Drop
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                handleFileSelect(files[0], preview, content, zone);
            }
        });
        
        // File input change
        input.addEventListener('change', function() {
            if (input.files.length > 0) {
                handleFileSelect(input.files[0], preview, content, zone);
            }
        });
    });
}

/**
 * Handle file selection and preview
 */
function handleFileSelect(file, previewElement, contentElement, zoneElement) {
    if (!previewElement) return;
    
    // Show preview, hide content
    if (contentElement) contentElement.style.display = 'none';
    previewElement.style.display = 'block';
    
    // Check file type
    const fileType = file.type;
    
    if (fileType.startsWith('image/')) {
        // Image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        
    } else if (fileType.startsWith('audio/')) {
        // Audio preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.innerHTML = `
                <audio controls>
                    <source src="${e.target.result}" type="${file.type}">
                    Your browser does not support the audio element.
                </audio>
                <p style="margin-top: 0.5rem; color: var(--text-secondary);">${file.name}</p>
            `;
        };
        reader.readAsDataURL(file);
        
    } else {
        // Generic file preview
        previewElement.innerHTML = `
            <i class="fas fa-file" style="font-size: 3rem; color: var(--accent-cyan);"></i>
            <p style="margin-top: 0.5rem;">${file.name}</p>
        `;
    }
    
    // Add a reset button
    const resetBtn = document.createElement('button');
    resetBtn.type = 'button';
    resetBtn.className = 'btn btn-secondary';
    resetBtn.style.marginTop = '1rem';
    resetBtn.innerHTML = '<i class="fas fa-trash"></i> Remove';
    resetBtn.onclick = function() {
        resetDropZone(zoneElement, contentElement, previewElement);
    };
    
    previewElement.appendChild(resetBtn);
}

/**
 * Reset drop zone to initial state
 */
function resetDropZone(zoneElement, contentElement, previewElement) {
    const input = zoneElement.querySelector('input[type="file"]');
    if (input) input.value = '';
    
    if (contentElement) contentElement.style.display = 'block';
    previewElement.style.display = 'none';
    previewElement.innerHTML = '';
}

/**
 * Flash Message Auto-Dismiss
 */
function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(element) {
    if (!element) return;
    
    let textToCopy;
    
    if (typeof element === 'string') {
        textToCopy = element;
    } else if (element.value !== undefined) {
        textToCopy = element.value;
    } else if (element.textContent !== undefined) {
        textToCopy = element.textContent;
    } else {
        return;
    }
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Show success feedback
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'error');
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    
    if (type === 'success') {
        notification.style.borderLeft = '4px solid var(--success)';
    } else if (type === 'error') {
        notification.style.borderLeft = '4px solid var(--danger)';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Form validation helper
 */
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'var(--danger)';
            
            // Remove error style on input
            input.addEventListener('input', function() {
                this.style.borderColor = '';
            }, { once: true });
        }
    });
    
    return isValid;
}

/**
 * Add CSS animations dynamically
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);
