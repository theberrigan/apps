// TODO: migrate to offscreen DOMParser
import { XMLParser } from './plugins/fxparser.min.js';



const ALARM_UPDATE_RATE = 'updateRate';
const CANVAS_SIZE = 64;
const RATE_RECORD_STORAGE_KEY = 'recordRate';
const NOTIFY_ABOUT_RECORD = true;
const PLAY_NOTIFICATION_SOUND = true;
const NOTIFICATION_SOUND_URL = chrome.runtime.getURL('sounds/notification.ogg'); 
const NOTIFICATION_VOLUME = 0.5; 



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


const fetchCBRate = (() => {
    const xmlParser = new XMLParser();

    return async () => {
        const url = 'https://www.cbr.ru/scripts/XML_daily_eng.asp';

        return fetch(url).then((response) => {
            return response.text();
        }).then((response) => {
            const data = xmlParser.parse(response);
            const currencies = data?.ValCurs?.Valute || [];
            const usdData = currencies.find(cur => cur.CharCode === 'USD');
            const rate = Number((usdData?.Value || '').replace(',', '.'));

            return Number.isFinite(rate) ? rate : 0;
        }).catch((reason) => {
            console.warn('Error:', reason);

            return 0;
        });
    };
})();


const fetchAlfaRate = async () => {
    const url = new URL('https://alfabank.ru/api/v1/scrooge/currencies/alfa-rates');

    url.searchParams.set('currencyCode.in', 'USD');
    url.searchParams.set('rateType.eq', 'makeCash');
    url.searchParams.set('lastActualForDate.eq', 'true');
    url.searchParams.set('clientType.eq', 'standardCC');
    url.searchParams.set('date.lte', (new Date()).toISOString());

    return fetch(url.toString(), {            
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    }).then((response) => {
        return response.json();
    }).then((response) => {
        const { data } = response;

        if (data) {
            let rates = data.find(item => item.currencyCode === 'USD')?.rateByClientType;

            if (rates) {
                rates = rates.find(item => item.clientType === 'standardCC')?.ratesByType;

                if (rates) {
                    rates = rates.find(item => item.rateType === 'makeCash')?.lastActualRate;

                    if (rates) {
                        const rate = rates.buy?.originalValue;

                        if (Number.isFinite(rate)) {
                            return rate;
                        }
                    }                    
                }
            }
        }

        return 0;
    }).catch((reason) => {
        console.warn('Error:', reason);

        return 0;
    });
};

const loadFonts = (() => {
    let isLoaded = false;

    return async () => {
        const family  = 'BNT';
        const fontUrl = chrome.runtime.getURL('fonts/BNT_digits.woff2'); 

        if (!isLoaded) {
            const font = new FontFace(family, `url(${ fontUrl })`, {
                style: 'normal',
                weight: 500,
                stretch: 'condensed'
            });

            await font.load();

            globalThis.fonts.add(font);

            isLoaded = true;
        }

        return family;
    }; 
})();

// https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D
// https://developer.chrome.com/docs/extensions/reference/action/
const onUpdateRates = (() => {    
    const canvas = new OffscreenCanvas(CANVAS_SIZE, CANVAS_SIZE);
    const ctx = canvas.getContext('2d', {
        alpha: true,
        willReadFrequently: true
    });

    const isYaBrowser = navigator.userAgent.includes('YaBrowser');

    ctx.imageSmoothingEnabled = true;
    ctx.fillStyle    = 'black';
    ctx.textBaseline = 'middle';
    ctx.textAlign    = 'center';

    let isUpdating = false;

    return async () => {
        if (isUpdating) {
            return;
        }

        isUpdating = true;

        const requestDate = formatDate(new Date());

        console.log('Requesting...', requestDate);

        const [ alfaRate, cbRate, fontFamilty ] = await Promise.all([
            fetchAlfaRate(),
            fetchCBRate(),
            loadFonts()
        ]);

        const rateText = String(Math.trunc(alfaRate));
        const fontSize = Math.trunc((rateText.length < 3 ? 80 : 64) * (isYaBrowser ? 0.8 : 1));

        ctx.font = `normal ${ fontSize }px ${ fontFamilty }`;

        ctx.fillText(
            rateText, 
            Math.trunc(CANVAS_SIZE * 0.5), 
            Math.trunc(CANVAS_SIZE * 0.5625)
        );

        chrome.action.setIcon({ 
            imageData: {
                [ String(CANVAS_SIZE) ]: ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE)
            }
        });

        chrome.action.setTitle({
            title: (
                `1 USD = ${ alfaRate.toFixed(2) } RUB (Альфа)\n` +
                `1 USD = ${ cbRate.toFixed(2) } RUB (ЦБ)\n` +
                `Обновлено: ${ requestDate }`
            )
        });

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        await checkRecord(alfaRate);

        isUpdating = false;
    };
})();

const checkRecord = async (newRate) => {    
    const oldRate = await getFromStorage(RATE_RECORD_STORAGE_KEY, 0.0);

    newRate = roundTo(newRate, 2);

    if (newRate > oldRate) {
        setToStorage(RATE_RECORD_STORAGE_KEY, newRate);

        notifyRateRecord(oldRate, newRate);
    }
};

const notifyRateRecord = (oldRate, newRate) => {
    if (!NOTIFY_ABOUT_RECORD) {
        return;
    }

    const id = crypto.randomUUID();

    chrome.notifications.create(id, {
        type: 'basic',
        iconUrl: chrome.runtime.getURL('images/alfa_logo.png'),
        title: 'Обновлён рекорд курса рубля',
        message: `Был: ${ oldRate.toFixed(2) }\nСтал: ${ newRate.toFixed(2) }`,
        silent: true
    });

    if (PLAY_NOTIFICATION_SOUND) {
        playNotificationSound();
    }

    setTimeout(() => {
        chrome.notifications.clear(id);
    }, 15000);
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

// https://developer.chrome.com/docs/extensions/reference/offscreen/
const createOffscreenDocument = async () => {
    if (await chrome.offscreen.hasDocument()) {
        return;
    }

    await chrome.offscreen.createDocument({
        url: chrome.runtime.getURL('html/offscreen.html'),
        reasons: [
            'AUDIO_PLAYBACK',
            // 'DOM_PARSER'
        ],
        justification: 'Notification sound playback'
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

const roundTo = (num, fraction) => {
    fraction = Math.pow(10, fraction);

    return Math.trunc(num * fraction) / fraction;
};

// -----------------------------------------------

chrome.action.onClicked.addListener(() => {
    onUpdateRates();
    // notifyRateRecord(12.35, 15.63);
});

chrome.alarms.onAlarm.addListener((alarm) => {
    switch (alarm.name) {
        case ALARM_UPDATE_RATE:
            onUpdateRates();
            break;
    }
});

// Alarms are permanent, so create them once on extension
// install event, after clearing the previous ones
chrome.runtime.onInstalled.addListener(async () => {
    await chrome.alarms.clearAll();

    chrome.alarms.create(ALARM_UPDATE_RATE, {        
        periodInMinutes: 60,  // Each alarm can be triggered no more than once per hour
        when: Date.now()      // Trigger it first time right now!
    });
});

chrome.runtime.onStartup.addListener(() => {
    onUpdateRates();
});

