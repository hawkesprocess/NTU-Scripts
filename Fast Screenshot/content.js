/**
 * Screenshot Extension - Content Script
 * Handles in-page notifications
 */

// Notification settings
const NOTIFICATION_STYLES = {
  base: {
    position: 'fixed',
    top: '20px',
    right: '20px',
    padding: '12px 20px',
    zIndex: '9999',
    borderRadius: '4px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
    fontFamily: 'system-ui, sans-serif',
    fontSize: '14px',
    color: 'white',
    transition: 'opacity 0.3s'
  },
  success: { backgroundColor: 'rgba(33, 150, 243, 0.9)' },
  error: { backgroundColor: 'rgba(217, 48, 37, 0.9)' }
};

// Listen for messages
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "notifyScreenshot") {
    showNotification(message.message || `Screenshot saved to screenshots/${message.domain}/ folder`, 'success');
  } else if (message.action === "notifyError") {
    showNotification(message.message, 'error');
  }
});

// Show notification
function showNotification(message, type) {
  const notification = document.createElement('div');
  
  // Apply styles
  Object.assign(notification.style, NOTIFICATION_STYLES.base);
  Object.assign(notification.style, NOTIFICATION_STYLES[type] || NOTIFICATION_STYLES.success);
  
  notification.textContent = message;
  document.body.appendChild(notification);
  
  // Auto remove after delay
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 3000);
} 