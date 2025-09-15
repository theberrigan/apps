import { fetchGameData } from './services/game-data.js';
import { setupRequestRules } from './network/requests.js';



chrome.runtime.onMessage.addListener(({ action, options }, _sender, sendResponse) => {
    (async () => {
        switch (action) {
            case 'FETCH_GAME_DATA':
                sendResponse(await fetchGameData(options));
                break;
        }        
    })();

    return true;
});

chrome.runtime.onInstalled.addListener(async () => {
    await setupRequestRules();
});

// TODO: debug only
// chrome.declarativeNetRequest.onRuleMatchedDebug.addListener((info) => {
//     console.log('Rule matched:', info.request.url, info);
// });
