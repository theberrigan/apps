const ALARM_SEARCH_VACANCIES = 'updateRate';
const VACANCY_CHECK_PERIOD = 5;  // minutes
const HH_ORIGIN = 'https://yaroslavl.hh.ru';
const VACANCIES_STORAGE_KEY = 'vacancies';
const NOTIFY_NEW_VACANCIES = true;
const PLAY_NOTIFICATION_SOUND = true;
const NOTIFICATION_SOUND_URL = chrome.runtime.getURL('sounds/notification.ogg'); 
const NOTIFICATION_VOLUME = 0.5; 
const NOTIFICATION_LIFETIME = 5 * 60 * 1000;
const ICON_MENU_VIEW_VACANCIES = 'icon_menu:view_vacancies';



const openVacanciesPage = () => {
    chrome.tabs.create({
        url: chrome.runtime.getURL('pages/vacancies.html')
    });
};

const formatDate = (() => {
    const formatter = new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'short', 
        year: 'numeric', 
        hour: 'numeric',
        minute: '2-digit'
    });

    return (date) => {
        date = (date instanceof Date) ? date : new Date(date);

        return formatter.format(date);
    };
})();

const notifyNewVacancies = (newVacancies) => {
    const newVacancyCount = newVacancies.length;

    if (!NOTIFY_NEW_VACANCIES || !newVacancyCount) {
        return;
    }

    const items = newVacancies.slice(0, 5).map(({ title }) => {
        return {
            title,
            message: ''
        };
    });

    const id = crypto.randomUUID();

    chrome.notifications.create(id, {
        type: 'list',
        title: `+${ newVacancyCount } новых вакансий`,
        message: '',
        iconUrl: chrome.runtime.getURL('images/icon_128.png'),
        silent: true,        
        priority: 2,
        requireInteraction: true,
        items,
        buttons: [
            {
                title: 'Просмотреть'
            }
        ]
    });

    if (PLAY_NOTIFICATION_SOUND) {
        playNotificationSound();
    }

    setTimeout(() => {
        chrome.notifications.clear(id);
    }, NOTIFICATION_LIFETIME);
};

// https://stackoverflow.com/questions/67437180/play-audio-from-background-script-in-chrome-extention-manifest-v3
const playNotificationSound = async () => {
    await createOffscreenDocument();

    await chrome.runtime.sendMessage({
        target: 'OFFSCREEN_DOCUMENT',
        action: 'PLAY_NOTIFICATION_SOUND',
        options: {
            soundUrl: NOTIFICATION_SOUND_URL,
            volume: NOTIFICATION_VOLUME
        }
    });
};

const fetchToken = async () => {
    let response = await fetch(HH_ORIGIN).then((response) => {
        if (!response.ok) {
            console.log('Failed to load page:', response);
            return null;
        }

        return response.text();
    }).catch((reason) => {
        console.log('Failed to load page:', reason);
        return null;
    });

    if (!response) {
        return null;
    }

    const match = response.match(/"xsrfToken"\s*:\s*"([^"]+)"/i);

    if (!match) {
        console.log('Failed to fetch XSRF token:', response);
        return null;            
    }

    return match[1];
};

const fetchVacanciesPage = async (token, query, page = 0) => {
    const url = new URL('/shards/vacancy/search', HH_ORIGIN);

    url.searchParams.set('text', query);
    url.searchParams.set('excluded_text', '');
    url.searchParams.set('work_format', 'REMOTE');
    url.searchParams.set('items_on_page', '100');
    url.searchParams.set('ored_clusters', 'true');
    url.searchParams.set('search_field', 'name');
    url.searchParams.set('enable_snippets', 'false');
    url.searchParams.set('hhtmFrom', 'vacancy_search_list');
    url.searchParams.set('hhtmFromLabel', 'vacancy_search_line');

    if (page > 0) {
        url.searchParams.set('page', String(page));
    }

    const referrer = new URL(url);

    referrer.pathname = '/search/vacancy';

    const response = await fetch(url, { 
        method: 'GET',
        mode: 'cors',
        credentials: 'include',
        referrer: referrer.toString(),
        headers: {
            'Accept': 'application/json',
            'Accept-Language': 'ru,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Priority': 'u=1, i',
            'X-hhtmfrom': 'vacancy_search_list',
            'X-hhtmsource': 'vacancy_search_list',
            'X-requested-with': 'XMLHttpRequest',
            'X-xsrftoken': token
        }
    }).then((response) => {
        if (!response.ok) {
            console.log('Failed to load vacancies:', response);
            return null;
        }

        return response.json();
    }).catch((reason) => {
        console.log('Failed to load vacancies:', reason);
        return null;
    });

    return response;
};

const wait = async (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};

const fetchVacancies = async (token, query) => {
    if (Array.isArray(query)) {
        query = query.map(v => String(v)).join(' OR ');
    }

    let result = [];
    let page   = 0;

    while (true) {
        const response = await fetchVacanciesPage(token, query, page);

        if (!response) {
            return null;
        }

        const { vacancies, paging, totalResults } = response.vacancySearchResult || {};

        if (!vacancies || !paging) {
            console.error(`'vacancies' or 'paging' is not found`);
            return null;            
        }

        if (page === 0) {
            console.log('Found:', totalResults);
        }

        result = result.concat(vacancies);

        const { next } = paging;

        if (!next || next.disabled) {
            break;
        }

        page = next.page;

        await wait(2000);
    }

    return result;
};

// https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D
// https://developer.chrome.com/docs/extensions/reference/action/
const onUpdateVacancies = (() => {
    let isUpdating = false;

    return async () => {
        if (isUpdating) {
            return;
        }

        isUpdating = true;

        const requestDate = formatDate(new Date());

        console.log('Requesting...', requestDate);

        const token = await fetchToken();

        if (!token) {
            return;
        }

        const vacancies = await fetchVacancies(token, [
            'frontend',
            'angular',
            'веб-разработчик',
            'web-разработчик',
        ]);

        if (!vacancies) {
            return;
        }

        const db = await getFromStorage(VACANCIES_STORAGE_KEY, {
            history: [],
            knownIds: []
        });

        const isHistoryNeeded = db.knownIds.length > 0;

        const history = [];

        for (let vacancy of vacancies) {
            if (!db.knownIds.includes(vacancy.vacancyId)) {
                db.knownIds.push(vacancy.vacancyId);

                if (isHistoryNeeded) {                    
                    history.push({
                        id:    vacancy.vacancyId,
                        title: vacancy.name,
                        url:   vacancy.links.desktop
                    });
                }
            }
        }

        if (history.length) {
            db.history.push(history);

            db.history = db.history.slice(-Math.trunc(24 * 60 / VACANCY_CHECK_PERIOD));
        }

        await setToStorage(VACANCIES_STORAGE_KEY, db);

        notifyNewVacancies(history);

        isUpdating = false;
    };
})();

// https://developer.chrome.com/docs/extensions/reference/offscreen/
const createOffscreenDocument = async () => {
    if (await chrome.offscreen.hasDocument()) {
        return;
    }

    await chrome.offscreen.createDocument({
        url: chrome.runtime.getURL('html/offscreen.html'),
        reasons: [
            'AUDIO_PLAYBACK',
            // 'DOM_PARSER',
        ],
        justification: 'Notification sound'
    });
};

// https://developer.chrome.com/docs/extensions/reference/storage/#type-StorageArea
const getFromStorage = async (key, defaultValue = null) => {
    const result = await chrome.storage.local.get(key);
    const value  = result[key];

    return value === undefined ? defaultValue : value;
};

const setToStorage = async (key, value) => {
    await chrome.storage.local.set({ [ key ]: value });
};

// -----------------------------------------------

chrome.action.onClicked.addListener(() => {
    onUpdateVacancies();
});

chrome.alarms.onAlarm.addListener((alarm) => {
    switch (alarm.name) {
        case ALARM_SEARCH_VACANCIES:
            onUpdateVacancies();
            break;
    }
});

// Alarms are permanent, so create them once on extension
// install event, after clearing the previous ones
chrome.runtime.onInstalled.addListener(async () => {
    await chrome.alarms.clearAll();

    chrome.alarms.create(ALARM_SEARCH_VACANCIES, {        
        periodInMinutes: VACANCY_CHECK_PERIOD,
        when: Date.now()
    });

    await chrome.contextMenus.removeAll();

    chrome.contextMenus.create({
        id: ICON_MENU_VIEW_VACANCIES,
        title: 'Просмотреть ваканси',
        contexts: [
            'action'
        ]
    });
});

chrome.runtime.onStartup.addListener(() => {
    onUpdateVacancies();
});

chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
    if (buttonIndex === 0) {
        openVacanciesPage();
    }

    chrome.notifications.clear(notificationId);
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === ICON_MENU_VIEW_VACANCIES) {
        openVacanciesPage();
    }
});

/*
        notifyNewVacancies([
{
            id:    1,
            title: 'Vacancy 1',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 2',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 3',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 4',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 5',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 6',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 7',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 8',
            url:   'sss'
        },{
            id:    2,
            title: 'Vacancy 9',
            url:   'sss'
        }
            ]);
*/