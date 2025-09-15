const ALARM_UPDATE_WEATHER = 'updateWeather';
const CANVAS_SIZE = 64;



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

const loadFonts = (() => {
    let isLoaded = false;

    return async () => {
        const family  = 'BNT';
        const fontUrl = chrome.runtime.getURL('fonts/big_noodle_titling.woff2'); 

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

const fetchWeather = async () => {
    const url = new URL('https://services.gismeteo.ru/inform-service/inf_chrome/forecast/');

    url.searchParams.set('city', '4313');  // 4313 - Ярославль
    url.searchParams.set('lang', 'ru');        

    return fetch(url, {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        headers: {
            'Accept': 'text/xml',
            'Accept-Language': 'ru,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    }).then((response) => {
        return response.text();
    }).then((response) => {
        return parseXML(response);
    }).catch((reason) => {
        console.warn('Error:', reason);

        return null;
    });
};

// https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D
// https://developer.chrome.com/docs/extensions/reference/action/
const onUpdateWeather = (() => {    
    const canvas = new OffscreenCanvas(CANVAS_SIZE, CANVAS_SIZE);
    const ctx = canvas.getContext('2d', {
        alpha: true,
        willReadFrequently: true
    });

    const isYaBrowser = navigator.userAgent.includes('YaBrowser');

    ctx.imageSmoothingEnabled = true;
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

        const [ weather, fontFamilty ] = await Promise.all([
            fetchWeather(),
            loadFonts()
        ]);

        let temperature = '--';
        let description = '';
        let color       = 'black';

        if (weather) {
            temperature = weather.temperature;
            description = weather.description;

            if (temperature > 0) {
                temperature = `+${ temperature }`;
            } else {
                temperature = `${ temperature }`;
            }
        }

        if (description) {
            description = `${ temperature }, ${ description }`;
        } else {
            description = temperature;            
        }

        const fontSize = Math.trunc((temperature.length < 3 ? 80 : 76) * (isYaBrowser ? 0.8 : 1));

        ctx.fillStyle = color;
        ctx.font      = `normal ${ fontSize }px ${ fontFamilty }`;

        ctx.fillText(
            temperature, 
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
                `Погода: ${ description }\n` +
                `Обновлено: ${ requestDate }`
            )
        });

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        isUpdating = false;
    };
})();

// https://stackoverflow.com/questions/67437180/play-audio-from-background-script-in-chrome-extention-manifest-v3
const parseXML = async (xml) => {
    await createOffscreenDocument();

    return chrome.runtime.sendMessage({
        target: 'OFFSCREEN_DOCUMENT',
        action: 'PARSE_XML',
        options: {
            xml
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
            'DOM_PARSER'
        ],
        justification: 'XML parsing'
    });
};

// -----------------------------------------------

chrome.action.onClicked.addListener(() => {
    onUpdateWeather();
});

chrome.alarms.onAlarm.addListener((alarm) => {
    switch (alarm.name) {
        case ALARM_UPDATE_WEATHER:
            onUpdateWeather();
            break;
    }
});

// Alarms are permanent, so create them once on extension
// install event, after clearing the previous ones
chrome.runtime.onInstalled.addListener(async () => {
    await chrome.alarms.clearAll();

    chrome.alarms.create(ALARM_UPDATE_WEATHER, {        
        periodInMinutes: 10,  // Each alarm can be triggered no more than once per hour
        when: Date.now()      // Trigger it first time right now!
    });
});

chrome.runtime.onStartup.addListener(() => {
    onUpdateWeather();
});

