let port = chrome.runtime.connectNative("com.nil.browser_control");

port.onMessage.addListener(async (message) => {
    if (message.action === "navigate") {
        let tabs = await chrome.tabs.query({active: true, currentWindow: true});
        if (tabs.length > 0) {
            chrome.tabs.update(tabs[0].id, {url: message.url}).catch(err => console.error(err));
        }
    } 
    
    else if (message.action === "reload") {
        let tabs = await chrome.tabs.query({active: true, currentWindow: true});
        if (tabs.length > 0) {
            chrome.tabs.reload(tabs[0].id);
        }
    } 
    
    // 3. SCREENSHOT -> WebP using OffscreenCanvas
    else if (message.action === "screenshot") {
        port.postMessage({action: "status", data: "Capturing..."});
        try {
            chrome.tabs.captureVisibleTab(null, {format: "png"}, async (pngDataUrl) => {
                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError);
                    return;
                }

                try {
                    // Convert Data URL to Bitmap
                    const response = await fetch(pngDataUrl);
                    const blob = await response.blob();
                    const bitmap = await createImageBitmap(blob);

                    // Draw on an OffscreenCanvas (Allowed in Service Workers)
                    const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(bitmap, 0, 0);

                    // Convert to WebP Blob
                    let webpBlob = await canvas.convertToBlob({ type: "image/webp", quality: 0.8 });

                    // Double Safety check for 1MB limit
                    if (webpBlob.size > 1000000) {
                        webpBlob = await canvas.convertToBlob({ type: "image/webp", quality: 0.4 });
                    }

                    // Convert Blob back to Data URL to send to Python
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        port.postMessage({
                            action: "screenshot_result",
                            data: reader.result
                        });
                    };
                    reader.readAsDataURL(webpBlob);
                    
                } catch (e) {
                    console.error("WebP Conversion failed:", e);
                }
            });
        } catch (error) {
            console.error("Capture failed: " + error);
        }
    }
});