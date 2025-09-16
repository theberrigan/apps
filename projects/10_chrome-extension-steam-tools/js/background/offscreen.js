export const createOffscreenDocument = async () => {
    if (await chrome.offscreen.hasDocument()) {
        return;
    }

    await chrome.offscreen.createDocument({
        url: chrome.runtime.getURL('html/offscreen.html'),
        reasons: [
            'DOM_PARSER',
            'IFRAME_SCRIPTING',
            'DOM_SCRAPING',
        ],
        justification: 'HTML parsing'
    });
};

export const executeOffscreen = async (action, options=null) => {
    await createOffscreenDocument();

    return chrome.runtime.sendMessage({
        target: 'OFFSCREEN_DOCUMENT',
        action,
        options
    });
};