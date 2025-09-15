chrome.runtime.onMessage.addListener(({ target, action, options }, _, sendResponse) => {
    if (target !== 'OFFSCREEN_DOCUMENT') {
        return;
    }

    switch (action) {
        case 'PARSE_XML':
            sendResponse(parseXML(options));
            break;
    }
});

const parseXML = ({ xml }) => {
    const dom = new DOMParser().parseFromString(xml, 'text/xml');

    const error = dom.querySelector(':scope > body > parsererror');

    if (error) {
        console.log('ERROR:', error);
        console.log(xml);

        return null;
    }

    const values = dom.querySelector(':scope > location > fact > values');

    if (!values) {
        console.log('ERROR: no \'values\' node found', dom);
        console.log(xml);

        return null;        
    }

    const temperature = Number(values.getAttribute('t'));
    const description = (values.getAttribute('descr') || '').trim();

    if (!Number.isFinite(temperature)) {
        console.log('ERROR: failed to parse temperature');
        console.log(xml);

        return null;         
    }

    return {
        temperature,
        description,
    };
};