// Service worker for Screenshot Extension

// Configuration constants
const RESTRICTED_URLS = ['chrome://', 'chrome-extension://', 'chrome-search://', 'edge://', 'about:', 'view-source:', 'file://'];

// Event Listeners
chrome.commands.onCommand.addListener(command => {
  if (command === 'take-screenshot') captureScreenshot();
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'takeScreenshot') {
    captureScreenshot()
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
  }
  return true; // Keep message channel open for async response
});

// Take and save screenshot
async function captureScreenshot() {
  try {
    // Get active tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0) throw new Error('No active tab found');
    
    const tab = tabs[0];
    
    // Check for restricted pages
    if (isRestrictedUrl(tab.url)) {
      const message = 'Cannot capture restricted page';
      notifyUser(tab.id, message, 'error');
      throw new Error(message);
    }
    
    // Capture screenshot
    const screenshot = await chrome.tabs.captureVisibleTab(null, { format: 'png' });
    if (!screenshot || screenshot.length < 100) throw new Error('Screenshot capture failed');
    
    // Save file
    const domain = getDomain(tab.url);
    const timestamp = getTimestamp();
    const filename = `screenshots/${domain}/${timestamp}.png`;
    
    await saveFile(screenshot, filename, tab.id, domain);
    return true;
  } catch (error) {
    console.error('Screenshot failed:', error);
    throw error;
  }
}

// Helper functions
function isRestrictedUrl(url) {
  return RESTRICTED_URLS.some(pattern => url.startsWith(pattern));
}

function getDomain(url) {
  try {
    return new URL(url).hostname || 'unknown-domain';
  } catch {
    return 'unknown-domain';
  }
}

function getTimestamp() {
  return new Date().toISOString().replace(/[:T]/g, '-').split('.')[0];
}

async function saveFile(dataUrl, filename, tabId, domain) {
  return new Promise((resolve, reject) => {
    chrome.downloads.download({
      url: dataUrl,
      filename: filename,
      saveAs: false
    }, downloadId => {
      if (chrome.runtime.lastError) {
        const error = chrome.runtime.lastError.message;
        notifyUser(tabId, 'Failed to save: ' + error, 'error');
        reject(new Error(error));
      } else {
        notifyUser(tabId, `Screenshot saved`, 'success', domain);
        resolve(downloadId);
      }
    });
  });
}

function notifyUser(tabId, message, type, domain = null) {
  chrome.tabs.sendMessage(tabId, { 
    action: type === 'error' ? 'notifyError' : 'notifyScreenshot',
    message: message,
    domain: domain
  });
}

// Service worker lifecycle
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', () => console.log('Screenshot service worker activated')); 