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

const extractElements = (html) => {
    const doc = parseXML(html);
    const els = [];

    if (doc) {
        for (let el of doc.body.children) {
            if (el.tagName === 'SCRIPT' && /var\s+sh\s*=/.test(el.innerHTML)) {
                const scriptEl = document.createElement('script');

                scriptEl.innerHTML = el.innerHTML;

                els.push(scriptEl);
            } else if (el.id === 'antiForgeryToken') {            
                els.push(el);
            }
        }
    }

    return els;
};

window.addEventListener('message', (e) => {    
    const { id, html } = e.data;

    document.body.append(...extractElements(html));

    e.source.postMessage({
        id,
        data: window.sh || null
    }, e.origin);
});