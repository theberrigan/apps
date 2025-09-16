// VK Flex Chrome Extension: vk.js

// chrome.runtime.sendMessage({ action: 'test' }, (s) => { console.log(s); });

// document.currentScript
if ([ 'vk.com', 'vk.ru' ].includes(window.location.hostname)) {
    let scriptNode = document.createElement('script');
    scriptNode.innerText = `window.vkfExtensionId = '${chrome.runtime.id}';`;
    document.head.appendChild(scriptNode);

    scriptNode = document.createElement('script');
    scriptNode.src = chrome.extension.getURL('assets/js/injection.js');
    document.head.appendChild(scriptNode);
}