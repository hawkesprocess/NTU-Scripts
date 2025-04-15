# Fast Screenshot

Wanted to quickly screenshot stuff to share to my friends so here is a Chrome extension that takes screenshots of webpages using customizable hotkeys and saves them to organized folders.

## Features

- Take instant screenshots with a keyboard shortcut (default: Alt+S)

## Installation

1. Download
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (top-right toggle)
4. Click "Load unpacked" and select the extension folder

## Usage

### Taking Screenshots
- Press Alt+S (or your custom hotkey) on any webpage
- Click the extension icon and use the "Take Screenshot Now" button

### Customizing Hotkeys
1. Click the extension icon
2. Select your preferred modifier key and main key
3. Click "Save Hotkey"
4. Go to `chrome://extensions/shortcuts` to apply your changes

## File Structure
- Screenshots are saved to: `Downloads/screenshots/[domain]/[timestamp].png`
- Example: `Downloads/screenshots/github.com/2023-04-15-10-30-45.png`

## Notes
- Can't take screenshots of chrome:// pages due to browser security restrictions
- All screenshots remain on your computer, nothing is uploaded
- Files are automatically organized by domain name 
