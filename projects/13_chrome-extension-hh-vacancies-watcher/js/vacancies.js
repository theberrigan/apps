const VACANCIES_STORAGE_KEY = 'vacancies';



const getFromStorage = async (key, defaultValue = null) => {
    const result = await chrome.storage.local.get(key);
    const value  = result[key];

    return value === undefined ? defaultValue : value;
};

const main = async () => {
    const db = await getFromStorage(VACANCIES_STORAGE_KEY);
    const history = db?.history;

    if (!Array.isArray(history)) {
        return;
    }

    const rootEl = document.createElement('div');

    rootEl.className = 'vacancies';

    history.reverse();

    console.log(history);

    history.forEach((group, _, groupIndex) => {
        const groupEl = document.createElement('ul');

        groupEl.className = 'vacancies__group';

        rootEl.append(groupEl);

        group.forEach(({ id, title, url }) => {
            const a = document.createElement('a');

            a.innerHTML = title;
            a.href = url
            a.target = '_blank';
            a.dataset.id = id;

            const itemEl = document.createElement('li');

            itemEl.className = 'vacancies__group-item';

            itemEl.append(a);

            groupEl.append(itemEl);
        });

    });

    document.body.querySelector('#content').append(rootEl);
};

main();