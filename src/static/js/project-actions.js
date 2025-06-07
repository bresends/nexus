/**
 * Project Actions JavaScript Module
 * Handles project-related UI interactions like copying project data
 */

// Global variables
let projectId;
let copyBtn;
let copyAllBtn;

/**
 * Set button state with visual feedback
 * @param {string} state - The state to set ('loading', 'success', 'error')
 * @param {string} originalText - The original button text to restore later
 */
function setButtonState(state, originalText) {
    // Store original text for restoration
    copyBtn.setAttribute('data-original-text', originalText);

    switch (state) {
        case 'loading':
            copyBtn.innerHTML = '<span class="material-icons action-button__icon">hourglass_empty</span> Loading...';
            copyBtn.disabled = true;
            break;
        case 'success':
            copyBtn.innerHTML = '<span class="material-icons action-button__icon">check</span> Copied!';
            copyBtn.style.backgroundColor = '#28a745';
            copyBtn.style.color = 'white';
            copyBtn.disabled = false;
            break;
        case 'error':
            copyBtn.innerHTML = '<span class="material-icons action-button__icon">error</span> Failed';
            copyBtn.style.backgroundColor = '#dc3545';
            copyBtn.style.color = 'white';
            copyBtn.disabled = false;
            break;
    }
}

/**
 * Reset button to its original state
 * @param {string} originalText - The original button text to restore
 */
function resetButtonState(originalText) {
    copyBtn.innerHTML = originalText;
    copyBtn.style.backgroundColor = '';
    copyBtn.style.color = '';
    copyBtn.disabled = false;
    copyBtn.removeAttribute('data-original-text');
}

/**
 * Copy text to clipboard with multiple fallback strategies
 * @param {string} text - The text to copy to clipboard
 * @returns {Promise} - Promise that resolves when text is copied
 */
async function copyToClipboard(text) {
    // Strategy 1: Modern Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
            await navigator.clipboard.writeText(text);
            console.log('✓ Copied using modern Clipboard API');
            return;
        } catch (err) {
            console.warn('Modern clipboard API failed:', err);
            // Continue to fallback methods
        }
    }

    // Strategy 2: Document.execCommand with better setup
    try {
        const success = await legacyClipboardCopy(text);
        if (success) {
            console.log('✓ Copied using legacy execCommand');
            return;
        }
    } catch (err) {
        console.warn('Legacy clipboard method failed:', err);
    }

    // Strategy 3: User-assisted manual copy
    console.log('Falling back to manual copy method');
    return manualCopyFallback(text);
}

/**
 * Legacy clipboard copy using execCommand with improved setup
 * @param {string} text - The text to copy
 * @returns {Promise<boolean>} - Promise that resolves to success status
 */
function legacyClipboardCopy(text) {
    return new Promise((resolve) => {
        try {
            // Create a more robust textarea element
            const textArea = document.createElement('textarea');
            
            // Set the text value
            textArea.value = text;
            
            // Style to make it invisible but accessible
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            textArea.style.width = '2em';
            textArea.style.height = '2em';
            textArea.style.padding = '0';
            textArea.style.border = 'none';
            textArea.style.outline = 'none';
            textArea.style.boxShadow = 'none';
            textArea.style.background = 'transparent';
            textArea.style.fontSize = '16px'; // Prevent zoom on iOS
            textArea.setAttribute('readonly', '');
            textArea.tabIndex = -1;
            
            // Add to DOM
            document.body.appendChild(textArea);
            
            // Select the text with multiple approaches
            textArea.focus();
            textArea.select();
            textArea.setSelectionRange(0, text.length);
            
            // Try to execute copy command
            let successful = false;
            try {
                successful = document.execCommand('copy');
            } catch (copyErr) {
                console.warn('execCommand copy failed:', copyErr);
            }
            
            // Clean up
            document.body.removeChild(textArea);
            
            resolve(successful);
            
        } catch (err) {
            console.warn('Legacy copy setup failed:', err);
            resolve(false);
        }
    });
}

/**
 * Manual copy fallback with user instruction
 * @param {string} text - The text to copy
 * @returns {Promise} - Promise that resolves when user interaction is complete
 */
function manualCopyFallback(text) {
    return new Promise((resolve) => {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = '9998';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        
        // Create modal
        const modal = document.createElement('div');
        modal.style.backgroundColor = 'white';
        modal.style.padding = '20px';
        modal.style.borderRadius = '8px';
        modal.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        modal.style.maxWidth = '90%';
        modal.style.maxHeight = '80%';
        modal.style.overflow = 'hidden';
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        
        // Create header
        const header = document.createElement('div');
        header.innerHTML = '<h4 style="margin: 0 0 15px 0; color: #333;">Copy Data</h4>';
        
        // Create instruction
        const instruction = document.createElement('div');
        instruction.innerHTML = 'The text below has been selected. Press <strong>Ctrl+C</strong> (or <strong>Cmd+C</strong> on Mac) to copy it:';
        instruction.style.marginBottom = '15px';
        instruction.style.color = '#666';
        
        // Create textarea with the data
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.width = '100%';
        textArea.style.height = '300px';
        textArea.style.border = '1px solid #ddd';
        textArea.style.borderRadius = '4px';
        textArea.style.padding = '10px';
        textArea.style.fontFamily = 'monospace';
        textArea.style.fontSize = '12px';
        textArea.style.resize = 'vertical';
        textArea.style.marginBottom = '15px';
        textArea.setAttribute('readonly', '');
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.innerHTML = 'Close';
        closeButton.style.backgroundColor = '#007bff';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.padding = '10px 20px';
        closeButton.style.borderRadius = '4px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.alignSelf = 'flex-end';
        
        // Assemble modal
        modal.appendChild(header);
        modal.appendChild(instruction);
        modal.appendChild(textArea);
        modal.appendChild(closeButton);
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Focus and select text
        setTimeout(() => {
            textArea.focus();
            textArea.select();
        }, 100);
        
        // Handle closing
        const cleanup = () => {
            if (overlay.parentNode) {
                document.body.removeChild(overlay);
            }
            resolve();
        };
        
        closeButton.addEventListener('click', cleanup);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                cleanup();
            }
        });
        
        // Close on Escape key
        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                cleanup();
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);
    });
}

/**
 * Final fallback method for copying text
 * @param {string} text - The text to copy
 * @param {Function} resolve - Promise resolve function
 * @param {Function} reject - Promise reject function
 */
function fallbackCopy(text, resolve, reject) {
    // Last resort: create a visible textarea briefly
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'absolute';
    textArea.style.left = '50%';
    textArea.style.top = '50%';
    textArea.style.transform = 'translate(-50%, -50%)';
    textArea.style.width = '300px';
    textArea.style.height = '100px';
    textArea.style.zIndex = '9999';
    textArea.style.backgroundColor = 'white';
    textArea.style.border = '2px solid #007bff';
    textArea.style.borderRadius = '4px';
    textArea.style.padding = '10px';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    // Show user instruction
    const instruction = document.createElement('div');
    instruction.innerHTML = 'Please press Ctrl+C (or Cmd+C on Mac) to copy the selected text, then click anywhere to close.';
    instruction.style.position = 'absolute';
    instruction.style.left = '50%';
    instruction.style.top = 'calc(50% + 60px)';
    instruction.style.transform = 'translateX(-50%)';
    instruction.style.backgroundColor = '#f8f9fa';
    instruction.style.padding = '10px';
    instruction.style.border = '1px solid #dee2e6';
    instruction.style.borderRadius = '4px';
    instruction.style.zIndex = '10000';
    instruction.style.maxWidth = '300px';
    instruction.style.textAlign = 'center';
    
    document.body.appendChild(instruction);
    
    // Clean up on click
    const cleanup = () => {
        if (textArea.parentNode) document.body.removeChild(textArea);
        if (instruction.parentNode) document.body.removeChild(instruction);
        document.removeEventListener('click', cleanup);
        resolve(); // Assume user copied successfully
    };
    
    setTimeout(() => {
        document.addEventListener('click', cleanup);
    }, 100);
}

/**
 * Handle copying project data to clipboard
 */
async function handleCopyProject() {
    try {
        // Show loading state
        const originalText = copyBtn.innerHTML;
        setButtonState('loading', originalText);

        // Fetch project data from JSON endpoint
        const response = await fetch(`/projects/${projectId}/json`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const projectData = await response.json();

        // Convert to formatted JSON string
        const jsonString = JSON.stringify(projectData, null, 2);

        // Copy to clipboard
        await copyToClipboard(jsonString);

        // Success feedback
        setButtonState('success', originalText);

        setTimeout(() => {
            resetButtonState(originalText);
        }, 2000);

    } catch (error) {
        console.error('Error copying project data:', error);

        // Error feedback
        const originalText = copyBtn.getAttribute('data-original-text') || copyBtn.innerHTML;
        setButtonState('error', originalText);

        setTimeout(() => {
            resetButtonState(originalText);
        }, 3000);

        alert('Failed to copy project data. Please try again or check your browser settings.');
    }
}

/**
 * Set button state for the "Copy All Projects" button with visual feedback
 * @param {string} state - The state to set ('loading', 'success', 'error')
 * @param {string} originalText - The original button text to restore later
 */
function setAllButtonState(state, originalText) {
    // Store original text for restoration
    copyAllBtn.setAttribute('data-original-text', originalText);

    switch (state) {
        case 'loading':
            copyAllBtn.innerHTML = '<span class="material-icons btn-icon">hourglass_empty</span> Loading...';
            copyAllBtn.disabled = true;
            break;
        case 'success':
            copyAllBtn.innerHTML = '<span class="material-icons btn-icon">check</span> Copied!';
            copyAllBtn.style.backgroundColor = '#28a745';
            copyAllBtn.style.color = 'white';
            copyAllBtn.disabled = false;
            break;
        case 'error':
            copyAllBtn.innerHTML = '<span class="material-icons btn-icon">error</span> Failed';
            copyAllBtn.style.backgroundColor = '#dc3545';
            copyAllBtn.style.color = 'white';
            copyAllBtn.disabled = false;
            break;
    }
}

/**
 * Reset the "Copy All Projects" button to its original state
 * @param {string} originalText - The original button text to restore
 */
function resetAllButtonState(originalText) {
    copyAllBtn.innerHTML = originalText;
    copyAllBtn.style.backgroundColor = '';
    copyAllBtn.style.color = '';
    copyAllBtn.disabled = false;
    copyAllBtn.removeAttribute('data-original-text');
}

/**
 * Handle copying all projects data to clipboard
 */
async function handleCopyAllProjects() {
    try {
        // Show loading state
        const originalText = copyAllBtn.innerHTML;
        setAllButtonState('loading', originalText);

        // Fetch all projects data from JSON endpoint
        const response = await fetch('/projects/all/json');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const allProjectsData = await response.json();

        // Convert to formatted JSON string
        const jsonString = JSON.stringify(allProjectsData, null, 2);

        // Copy to clipboard
        await copyToClipboard(jsonString);

        // Success feedback
        setAllButtonState('success', originalText);

        setTimeout(() => {
            resetAllButtonState(originalText);
        }, 2000);

    } catch (error) {
        console.error('Error copying all projects data:', error);

        // Error feedback
        const originalText = copyAllBtn.getAttribute('data-original-text') || copyAllBtn.innerHTML;
        setAllButtonState('error', originalText);

        setTimeout(() => {
            resetAllButtonState(originalText);
        }, 3000);

        alert('Failed to copy all projects data. Please try again or check your browser settings.');
    }
}

/**
 * Initialize project actions functionality
 */
function initProjectActions() {
    // Get project ID from the page
    projectId = window.PROJECT_ID || document.body.getAttribute('data-project-id');
    copyBtn = document.getElementById('copyProjectBtn');
    copyAllBtn = document.getElementById('copyAllProjectsBtn');

    if (projectId && copyBtn) {
        copyBtn.addEventListener('click', handleCopyProject);
    }

    if (copyAllBtn) {
        copyAllBtn.addEventListener('click', handleCopyAllProjects);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initProjectActions);
