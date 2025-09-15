const DISCARD_TAB_ITEM_ID = 'discard_tab';

const discardTab = async (tab) => {
    if (/^(chrome|browser):\/\//.test(tab.url)) {
        return;
    }

    const discardedTab = await chrome.tabs.discard(tab.id);

    console.log('Tab has been discarded:', discardedTab);
};

const addContextMenuItems = async () => {
    await chrome.contextMenus.removeAll();

    await chrome.contextMenus.create({
        id: DISCARD_TAB_ITEM_ID,
        type: 'normal',
        title: 'Выгрузить вкладку',
        contexts: [ 'page' ],
        enabled: true,
        visible: true,
    });
};

const executeCommand = async (command, tab) => {
    switch (command) {
        case DISCARD_TAB_ITEM_ID: {
            await discardTab(tab);
            break;
        }
    }
};

chrome.runtime.onInstalled.addListener(async () => {
    await addContextMenuItems();
});

chrome.contextMenus.onClicked.addListener(async (e, tab) => {
    await executeCommand(e.menuItemId, tab);
});

chrome.commands.onCommand.addListener(async (command, tab) => {
    await executeCommand(command, tab);
});
