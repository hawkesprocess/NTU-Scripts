// Initialize on DOM load with event listeners and saved settings
document.addEventListener('DOMContentLoaded', () => {
  // Set up event listeners
  document.getElementById('save-hotkey').addEventListener('click', saveHotkey);
  document.getElementById('take-screenshot').addEventListener('click', takeScreenshot);
  
  // Load saved settings
  chrome.storage.sync.get(['hotkeyConfig'], (result) => {
    const config = result.hotkeyConfig || { modifier1: 'Alt', key: 'S' };
    document.getElementById('modifier1').value = config.modifier1;
    document.getElementById('key').value = config.key;
    document.getElementById('current-hotkey').textContent = `${config.modifier1}+${config.key}`;
  });
});

// Save hotkey settings 
function saveHotkey() {
  const modifier1 = document.getElementById('modifier1').value;
  const key = document.getElementById('key').value.toUpperCase();
  
  if (!key) {
    alert('Please enter a main key');
    return;
  }
  
  chrome.storage.sync.set({ hotkeyConfig: { modifier1, key } }, () => {
    document.getElementById('current-hotkey').textContent = `${modifier1}+${key}`;
    alert('Hotkey saved! Update Chrome shortcuts at chrome://extensions/shortcuts');
  });
}

// Take screenshot via background script
function takeScreenshot() {
  const button = document.getElementById('take-screenshot');
  const originalText = button.textContent;
  
  // Show loading state
  button.textContent = 'Taking screenshot...';
  button.disabled = true;
  
  chrome.runtime.sendMessage({ action: 'takeScreenshot' }, (response) => {
    if (chrome.runtime.lastError || (response && !response.success)) {
      // Show error
      const errorMsg = chrome.runtime.lastError ? 
                       chrome.runtime.lastError.message : 
                       (response ? response.error : 'Unknown error');
      alert('Screenshot failed: ' + errorMsg);
      
      // Reset button
      button.textContent = originalText;
      button.disabled = false;
    } else {
      // Success - close popup
      setTimeout(() => window.close(), 300);
    }
  });
} 