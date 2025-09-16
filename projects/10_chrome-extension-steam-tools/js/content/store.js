const formatTime = (sec) => {
    if (sec < 60) {
        return String(Math.trunc(sec)) + 's';
    } else if (sec < 3600) {
        return String(Math.trunc(sec / 60)) + 'm';
    } else {
        return (sec / 3600).toFixed(1) + 'h';
    }
}

const modifySidebar = (sidebarEl) => {
    const selectors = [
        ':scope > .block.recommendation_noinfo',
        ':scope > .block.heading:has(+ .block.recommendation_noinfo)',
        ':scope > .block.recommendation_reasons',
        ':scope > .block.heading:has(+ .block.recommendation_reasons)',
        ':scope > .block:has(> .communitylink_points_shop_images)',
        ':scope > .block#shareEmbedRow',
        ':scope > .block > [data-featuretarget=\'store-sidebar-controller-support-info\']',
    ];

    sidebarEl.querySelectorAll(selectors.join(', ')).forEach((el) => {
        el.remove();
    });

    const achEl = sidebarEl.querySelector(':scope > #achievement_block');

    if (achEl) {
        sidebarEl.prepend(achEl);
    }
};

const main = async () => {
    const pageUrl = globalThis.location.href;

    const match = pageUrl.match(/^https?:\/\/store\.steampowered\.com\/app\/(\d+)/);

    if (!match) {
        return;
    }

    const appId = Number(match[1]);

    const appNameEl = document.body.querySelector('#appHubAppName');
    const sidebarEl = document.body.querySelector('.rightcol.game_meta_data');

    if (!appNameEl || !sidebarEl) {
        return;
    }

    modifySidebar(sidebarEl);

    const appName = appNameEl.textContent.trim();

    if (!Number.isFinite(appId) || !appName) {
        return;
    }

    const response = await chrome.runtime.sendMessage({
        action: 'FETCH_GAME_DATA',
        options: {
            appId,
            appName
        }
    });

    const hltbData = response.hltb;
    const shData   = response.steamHunters;

    console.log(response);

    if (!hltbData) {
        return;
    }

    const hltbAppId = hltbData.id;

    const blockEl = document.createElement('div');

    blockEl.className = 'block responsive_apppage_details_right stex-block';

    // -----

    const links = [
        {
            text: 'How Long to Beat',
            url: `https://howlongtobeat.com/game/${ hltbAppId }`,
        },
        {
            text: 'SteamHunters',
            url: `https://steamhunters.com/apps/${ appId }/achievements`,
        }
    ]

    const linkItems = [];

    for (let [ i, { text, url } ] of links.entries()) {
        if (i > 0) {
            const spanEl = document.createElement('span');

            spanEl.className   = 'stex-block__link-sep';
            spanEl.textContent = '|';

            linkItems.push(spanEl);
        }

        const linkEl = document.createElement('a');

        linkEl.className   = 'stex-block__link';
        linkEl.textContent = text;
        linkEl.href        = url;
        linkEl.rel         = 'nofollow noopener';
        linkEl.target      = '_blank';

        linkItems.push(linkEl);
    }

    blockEl.append(...linkItems);

    // -----

    const tableEl = document.createElement('table');

    tableEl.className = 'stex-block__table';

    const tbodyEl = document.createElement('tbody');

    tableEl.append(tbodyEl);

    const timings = [
        {
            name: 'Main Story:',
            time: formatTime(hltbData.time.main)
        },
        {
            name: 'Main + Extras:',
            time: formatTime(hltbData.time.plus)
        },
        {
            name: 'Completionist:',
            time: formatTime(hltbData.time.full)
        },
    ];

    if (shData) {
        timings.push({
            name: 'Achievements:',
            time: formatTime(shData.medianTime)
        });

        timings.push({
            name: 'Has paid DLC:',
            time: shData.hasPaidDLC ? 'Yes' : 'No'
        });
    }

    for (let { name, time } of timings) {
        const trEl = document.createElement('tr');
        const thEl = document.createElement('th');
        const tdEl = document.createElement('td');

        thEl.textContent = name;
        tdEl.textContent = time;

        trEl.append(thEl);
        trEl.append(tdEl);

        tbodyEl.append(trEl);
    }

    blockEl.append(tableEl);

    // -----

    sidebarEl.prepend(blockEl);

    return true;
};

main();