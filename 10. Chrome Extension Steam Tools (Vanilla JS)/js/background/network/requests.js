import { USER_AGENT, EXT_ID } from '../common.js';



const ALL_RESOURCE_TYPES = Object.values(chrome.declarativeNetRequest.ResourceType);

export const setupRequestRules = async () => {
    const rulesToRemove = await chrome.declarativeNetRequest.getDynamicRules();
    const idsToRemove   = rulesToRemove.map((rule) => rule.id);

    const rulesToAdd = [
        {
            id: 1,
            priority: 1,
            action: {
                type: 'modifyHeaders',
                requestHeaders: [
                    {
                        header: 'referer',
                        operation: 'set',
                        value: 'https://howlongtobeat.com/'
                    },
                    {
                        header: 'origin',
                        operation: 'set',
                        value: 'https://howlongtobeat.com/'
                    },
                    {
                        header: 'user-agent',
                        operation: 'set',
                        value: USER_AGENT
                    },
                ]
            },
            condition: {
                requestDomains: [
                    'howlongtobeat.com'
                ],
                initiatorDomains: [
                    EXT_ID
                ],
                resourceTypes: ALL_RESOURCE_TYPES
            }
        }
    ];

    await chrome.declarativeNetRequest.updateDynamicRules({
        removeRuleIds: idsToRemove,
        addRules: rulesToAdd
    });
};
