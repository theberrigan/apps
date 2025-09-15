const parseXML = (xml, type='text/html') => {
    const doc = new DOMParser().parseFromString(xml, type);

    const error = doc.querySelector(':scope > body > parsererror');

    if (error) {
        console.log('ERROR:', error);
        console.log(xml.slice(0, 100));

        return null;
    }

    return doc;
};

const extractHLTBConfig = ({ html }) => {
    const doc = parseXML(html);

    if (!doc) {
        return null;
    }

    const scriptEl = doc.querySelector('script#__NEXT_DATA__');

    if (!scriptEl) {
        return null;
    }

    return scriptEl.textContent.trim();
};

const extractSHGameData = ({ html }) => {
    const doc = parseXML(html);

    if (!doc) {
        return null;
    }

    let medianTime = null;
    let hasPaidDLC = false;
    
    const columns = doc.body.querySelectorAll(':scope > main > .banner .media-body .media-body > ul > li');

    if (!columns.length) {
        return null;
    }

    const linkEls = columns[0].querySelectorAll(':scope > div.d-table > a');

    if (!linkEls.length) {
        return null;
    }

    for (let linkEl of linkEls) {
        // linkEl = linkEl.cloneNode(true);
        
        const spanEl = linkEl.querySelector(':scope > span');

        if (!spanEl) {
            continue;
        }
        
        const iconEl = spanEl.querySelector(':scope > i');

        if (iconEl) {
            iconEl.remove();
        }

        const spanText = spanEl.textContent.trim();

        spanEl.remove();

        const linkText = linkEl.textContent.trim();

        if (linkText === 'Median Completion Time') {
            medianTime = spanText;

            const match = medianTime.match(/^(?:([\d\s]+)h\s*)?(?:([\d\s]+)m)?$/i);

            if (match && match[1] && match[2]) {
                const h = parseInt((match[1] || '0').replace(/\s+/g, ''), 10);
                const m = parseInt((match[2] || '0').replace(/\s+/g, ''), 10);

                medianTime = h * 3660 + m * 60;  // seconds
            }

            break;
        }
    }

    const itemEls = columns[1]?.querySelectorAll(':scope > ul > li');

    if (itemEls) {
        for (let itemEl of itemEls) {
            // itemEl = itemEl.cloneNode(true);

            itemEl.querySelector(':scope > i')?.remove();

            const itemText = itemEl.textContent.trim();

            if (itemText === 'Paid DLC') {
                hasPaidDLC = true;
                break;
            }
        }
    }

    return {
        medianTime,
        hasPaidDLC,
    };
};

const extractSHAPIToken = ({ html }) => {
    const doc = parseXML(html);

    if (!doc) {
        return null;
    }

    const inputEl = doc.body.querySelector(`input[name='__RequestVerificationToken']`);  // #antiForgeryToken >

    const token = (inputEl?.value || '').trim();

    return token || null;
};

const createTimer = (time, value) => {
    return new Promise((resolve) => {
        setTimeout(() => resolve(value), time);
    });
};

const timedTasks = (time, timeoutValue, ...tasks) => {
    return Promise.race([
        createTimer(time, timeoutValue),
        ...tasks
    ]);
};

const extractSHFullGameData = async ({ html }) => {
    const iframe = document.createElement('iframe');

    const responseTask = new Promise((resolve) => {
        const messageId = crypto.randomUUID();

        iframe.addEventListener('load', () => {
            iframe.contentWindow.postMessage({
                id: messageId,
                html
            }, '*');
        });

        window.addEventListener('message', (e) => {
            const { id, data } = e.data;

            if (id !== messageId) {
                return;
            }

            iframe.remove();

            resolve(data);
        });
    });

    iframe.src = '../../html/sandbox.html';

    document.body.append(iframe);

    return timedTasks(3000, null, responseTask);
};

chrome.runtime.onMessage.addListener(({ target, action, options }, _, sendResponse) => {
    (async () => {
        if (target !== 'OFFSCREEN_DOCUMENT') {
            return;
        }

        switch (action) {
            case 'HLTB_EXTRACT_CONFIG':
                sendResponse(extractHLTBConfig(options));
                break;
            case 'SH_EXTRACT_API_TOKEN':
                sendResponse(extractSHAPIToken(options));
                break;
            case 'SH_EXTRACT_GAME_DATA':
                sendResponse(extractSHGameData(options));
                break;
            case 'SH_EXTRACT_FULL_GAME_DATA':
                sendResponse(await extractSHFullGameData(options));
                break;
        }
    })();

    return true;
});