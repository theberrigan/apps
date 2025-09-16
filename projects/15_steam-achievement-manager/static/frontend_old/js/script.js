const isNumeric = (value) => {
    return /^\d+$/.test(String(value));
};

class Achievements {
    constructor (urlForm) {
        this.urlForm = urlForm;
        this.rootEl = document.querySelector('.achievements');
        this.filterAchieveEl = this.rootEl.querySelector('.achievements__filter-achieve');
        this.filterSortEl = this.rootEl.querySelector('.achievements__filter-sort-dropdown');
        this.filterSortButtonEls = this.rootEl.querySelectorAll('.achievements__filter-sort-button');
        this.copyButtonEl = this.rootEl.querySelector('.achievements__filters-copy');
        this.downloadButtonEl = this.rootEl.querySelector('.achievements__filters-download');
        this.tableEl = this.rootEl.querySelector('.achievements__table');
        this.statsTableEl = this.rootEl.querySelector('.achievements__stats-table');
        this.metaTitle = this.rootEl.querySelector('.achievements__meta-title');
        this.metaDescription = this.rootEl.querySelector('.achievements__meta-description');        

        this.valueEls = {
            playerProfile: this.rootEl.querySelector('#player_profile'),
            playerSteamId: this.rootEl.querySelector('#player_steam_id'),
            appName: this.rootEl.querySelector('#app_name'),
            guidesGoogle: this.rootEl.querySelector('#guides_google'),
            guidesSteam: this.rootEl.querySelector('#guides_steam'),
            guidesSteamHunters: this.rootEl.querySelector('#guides_sh'),
            guidesPCGW: this.rootEl.querySelector('#guides_pcgw'),
            appId: this.rootEl.querySelector('#app_id'),
            appSlug: this.rootEl.querySelector('#app_slug'),
            hoursPlayed: this.rootEl.querySelector('#hours_played'),
            mpScore: this.rootEl.querySelector('#has_mp'),
            hltb: this.rootEl.querySelector('#hltb'),
            hltbLink: this.rootEl.querySelector('#hltb_link'),
            hltbStats: this.rootEl.querySelector('#hltb_stats'),
            headerImage: this.rootEl.querySelector('#header_image'),
            totalAchievements: this.rootEl.querySelector('#total_achievements'),
            unlockedAchievements: this.rootEl.querySelector('#unlocked_achievements'),
            percentAchievements: this.rootEl.querySelector('#percent_achievements'),
        };

        this.data = null;

        this.filterAchieveEl.addEventListener('change', () => {
            if (this.data) {
                this.data.achievements = this.indexAchievements(this.filterAchievements(this.data.achievements));
                this.updateTable();
                this.urlForm.saveState();
            }
        });

        this.filterSortEl.addEventListener('change', () => {
            if (this.data) {
                this.data.achievements = this.indexAchievements(this.sortAchievements(this.data.achievements));
                this.updateTable();
                this.urlForm.saveState();
            }
        });

        this.filterSortButtonEls.forEach((btnEl) => {
            btnEl.addEventListener('click', () => {
                this.filterSortButtonEls.forEach((btn2El) => {
                    if (btnEl === btn2El) {
                        btn2El.classList.remove('btn-outline-secondary');
                        btn2El.classList.add('btn-secondary');
                        this.filterSortEl.dataset.order = btn2El.dataset.order;
                    } else {
                        btn2El.classList.add('btn-outline-secondary');
                        btn2El.classList.remove('btn-secondary');
                    }
                });

                this.data.achievements = this.indexAchievements(this.sortAchievements(this.data.achievements));
                this.updateTable();
                this.urlForm.saveState();
            });
        });

        this.downloadButtonEl.addEventListener('click', () => {
            const content = this.getPlainList();

            if (content.length) {
                const fileName = this.data.game.name.replace(/[\\\/\:\*\?\"\<\>\|]+/g, '');

                const file = new File([ content ], `${ fileName }.txt`, {
                    type: 'text/plain',
                });

                const link = document.createElement('a');
                const url = URL.createObjectURL(file);

                link.href = url;
                link.download = file.name;

                document.body.appendChild(link);

                link.click();

                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }
        });

        this.copyButtonEl.addEventListener('click', () => {
            const content = this.getPlainList();

            if (content.length) {
                navigator.clipboard.writeText(content);
            }
        });
    }

    getPlainList () {        
        if (this.data?.achievements?.length) {
            const content = this.data.achievements.filter((achievement) => {
                return !achievement.el.hidden;
            }).map((achievement) => {
                return `- ${ achievement.name } -- ${ achievement.description }`;
            });

            if (content.length) {
                return content.join('\n');
            }
        }

        return null;
    }

    getGoogleAchievementUrl (gameName, achName) {        
        const url = new URL('https://www.google.com/search');

        url.searchParams.set('q', `${ gameName } ${ achName } achievement`);

        return url.toString();
    }

    getGoogleGuidesUrl (gameName) {        
        const url = new URL('https://www.google.com/search');

        url.searchParams.set('q', gameName + ' achievement guide');

        return url.toString();
    }

    getSteamGuidesUlr (gameId) {
        return `https://steamcommunity.com/app/${ gameId }/guides/?searchText=achievements&browsefilter=trend`;
    }

    getSteamHuntersGuidesUrl (gameId) {
        return `https://steamhunters.com/apps/${ gameId }/achievements`;
    }

    getPCGWGuidesUrl (gameName) {
        const url = new URL('https://www.pcgamingwiki.com/w/index.php');

        url.searchParams.set('search', gameName);

        return url.toString();
    }

    formatTime (sec) {
        if (sec < 60) {
            return String(Math.trunc(sec)) + 's';
        } else if (sec < 3600) {
            return String(Math.trunc(sec / 60)) + 'm';
        } else {
            return (sec / 3600).toFixed(1) + 'h';
        }
    }

    applyData (data) {
        if (data) {
            const mpScoreMap = {
                0: 'No',
                1: '<strong style="color: #ffb831;">Yes<strong>',
                2: '<strong style="color: #ff3131;">Yes<strong>',
            };

            const totalAchs = data.achievements.length;
            const unlockedAchs = data.achievements.filter(ach => ach.isAchieved).length;

            this.valueEls.playerProfile.innerHTML = data.player.profileName;
            this.valueEls.playerSteamId.innerHTML = data.player.steamId;
            this.valueEls.appName.innerHTML = data.game.name;
            this.valueEls.appName.href = `https://store.steampowered.com/app/${ data.game.id }`;
            this.valueEls.appId.innerHTML = data.game.id;
            this.valueEls.appSlug.innerHTML = data.game.slug;
            this.valueEls.hoursPlayed.innerHTML = data.stats.hoursPlayed;
            this.valueEls.mpScore.innerHTML = mpScoreMap[data.game.mpScore] || 'Unknown';
            this.valueEls.guidesGoogle.href = this.getGoogleGuidesUrl(data.game.name);
            this.valueEls.guidesSteam.href = this.getSteamGuidesUlr(data.game.id);
            this.valueEls.guidesSteamHunters.href = this.getSteamHuntersGuidesUrl(data.game.id);
            this.valueEls.guidesPCGW.href = this.getPCGWGuidesUrl(data.game.name);
            this.valueEls.totalAchievements.innerHTML = totalAchs;
            this.valueEls.unlockedAchievements.innerHTML = unlockedAchs;
            this.valueEls.percentAchievements.innerHTML = Math.round(unlockedAchs / totalAchs * 100);

            if (data.hltb) {
                const { id, main, plus, full } = data.hltb;

                this.valueEls.hltb.style.removeProperty('display');
                this.valueEls.hltbLink.href = `https://howlongtobeat.com/game/${ id }`;
                this.valueEls.hltbStats.innerHTML = (
                    `<span title="Main Story">${ this.formatTime(main) }</span>` + 
                    ' | ' +
                    `<span title="Main + Extras">${ this.formatTime(plus) }</span>` + 
                    ' | ' +
                    `<span title="Completionist">${ this.formatTime(full) }</span>`
                );
            } else {
                this.valueEls.hltb.style.display = 'none';
                this.valueEls.hltbLink.href = '';
                this.valueEls.hltbStats.innerHTML = '';
            }

            this.metaTitle.innerHTML = data.game.name || '';
            this.metaDescription.innerHTML = data.game.description || '';

            this.valueEls.headerImage.src = data.game.headerURL || '';

            if (data.bgUrl) {
                document.body.style.backgroundImage = `url('${ data.bgUrl }')`;
            } else {
                document.body.style.removeProperty('background-image');
            }

            const tbodyEl = document.createElement('tbody');

            data.achievements.forEach((achievement) => {
                const { id, name, description, isAchieved, achieveDate, achievedIconURL, unachievedIconURL, globalPercent } = achievement;

                const trEl = achievement.el = document.createElement('tr');

                trEl.className = 'achievement';

                trEl.dataset.id = id;
                trEl.dataset.isAchieved = String(isAchieved);

                const td1El = document.createElement('td');

                td1El.className = 'achievement__img-cell';

                const imgEl = document.createElement('img');

                imgEl.className = 'achievement__img';

                imgEl.src = isAchieved ? achievedIconURL : unachievedIconURL;

                td1El.appendChild(imgEl);
                trEl.appendChild(td1El);

                const td2El = document.createElement('td');
                const indexEl = document.createElement('span');

                indexEl.className = 'achievement__index';

                td2El.appendChild(indexEl);

                let nameEl = document.createElement('a');

                nameEl.target = '_blank';
                nameEl.rel = 'nofollow noopener';
                nameEl.href = this.getGoogleAchievementUrl(data.game.name, name);
                nameEl.title = id;
                nameEl.innerHTML = name;                
                nameEl.className = 'achievement__name';

                if (isAchieved) {
                    nameEl.classList.add('achievement__name_achieved');
                }

                td2El.appendChild(nameEl);

                if (globalPercent !== null) {
                    const percentEl = document.createElement('span');

                    if (globalPercent < 10) {
                        percentEl.className = 'badge bg-warning text-dark achievement__badge';
                    } else {
                        percentEl.className = 'badge bg-secondary text-light achievement__badge';
                    }

                    percentEl.innerHTML = `Global ${ Math.trunc(globalPercent * 10) / 10 }%`;

                    td2El.appendChild(percentEl);
                }

                if (isAchieved) {
                    const dateEl = document.createElement('span');

                    dateEl.className = 'badge bg-secondary text-light achievement__badge';

                    if (achieveDate) {
                        dateEl.innerHTML = `Achieved ${ new Date(achieveDate * 1000).toLocaleString() }`;
                    } else {
                        dateEl.innerHTML = 'Achieved';
                    }

                    td2El.appendChild(dateEl);
                }

                const descrEl = document.createElement('div');

                descrEl.innerHTML = description;

                td2El.appendChild(descrEl);

                trEl.appendChild(td2El);

                // tbodyEl.appendChild(trEl);
            });

            data.achievements = this.indexAchievements(this.filterAchievements(this.sortAchievements(data.achievements)));

            data.achievements.forEach((achievement) => {
                tbodyEl.appendChild(achievement.el);
            });

            this.tableEl.innerHTML = '';
            this.tableEl.appendChild(tbodyEl);

            // -----------------------------------------------

            const ingameStats = data.stats.ingame || [];

            if (ingameStats.length) {
                const tbodyEl = document.createElement('tbody');

                ingameStats.forEach(({ name, value }) => {
                    const trEl  = document.createElement('tr');
                    const td1El = document.createElement('td');
                    const td2El = document.createElement('td');

                    td1El.textContent = name;
                    td2El.textContent = String(value);

                    trEl.appendChild(td1El);
                    trEl.appendChild(td2El);
                    tbodyEl.appendChild(trEl);
                });

                this.statsTableEl.innerHTML = '';
                this.statsTableEl.appendChild(tbodyEl);
                this.statsTableEl.hidden = false;
            } else {
                this.statsTableEl.innerHTML = '';
                this.statsTableEl.hidden = true;
            }

            // -----------------------------------------------

            this.data = data;
            this.rootEl.hidden = false;
        } else {
            this.valueEls.playerProfile.innerHTML = '';
            this.valueEls.playerSteamId.innerHTML = '';
            this.valueEls.appName.innerHTML = '';
            this.valueEls.appId.innerHTML = '';
            this.valueEls.appSlug.innerHTML = '';
            this.valueEls.hoursPlayed.innerHTML = '';
            this.valueEls.mpScore.innerHTML = '';
            this.valueEls.hltb.style.display = 'none';
            this.valueEls.hltbLink.href = '';
            this.valueEls.hltbStats.innerHTML = '';
            this.valueEls.totalAchievements.innerHTML = '';
            this.valueEls.unlockedAchievements.innerHTML = '';
            this.valueEls.percentAchievements.innerHTML = '';
            this.tableEl.innerHTML = '';
            this.valueEls.headerImage.src = '';
            this.metaTitle.innerHTML = '';
            this.metaDescription.innerHTML = '';
            this.statsTableEl.innerHTML = '';
            this.statsTableEl.hidden = true;

            document.body.style.removeProperty('background-image');

            this.data = null;
            this.rootEl.hidden = true;
        }
    }

    filterAchievements (achievements) {
        const value = this.filterAchieveEl.value;

        achievements.forEach((achievement) => {
            achievement.el.hidden = (value === 'achieved' && !achievement.isAchieved) || (value === 'unachieved' && achievement.isAchieved);
        });

        return achievements;
    }

    sortAchievements (achievements) {
        const key = this.filterSortEl.value;
        const order = Number(this.filterSortEl.dataset.order);

        switch (key) {
            case 'id':
            case 'name':
                return achievements.sort((a, b) => a[key].localeCompare(b[key]) * order);
            case 'achieveDate':
            case 'globalPercent':
                return achievements.sort((a, b) => (a[key] - b[key]) * order);                
        }
    }

    indexAchievements (achievements) {
        let index = 0;

        achievements.forEach((achievement) => {
            if (!achievement.el.hidden) {
                achievement.el.querySelector('.achievement__index').innerHTML = `${ ++index }.&nbsp;`;
            }
        });

        return achievements;
    }

    updateTable () {
        const tbodyEl = document.createElement('tbody');

        this.data.achievements.forEach((achievement) => {
            tbodyEl.appendChild(achievement.el);
        });

        this.tableEl.innerHTML = '';
        this.tableEl.appendChild(tbodyEl);
    }
}


class URLForm {
    constructor () {
        this.achievements = new Achievements(this);

        this.isValid = false;
        this.isSubmitting = false;

        this.formEl = document.querySelector('.url-form');
        this.fieldsetEl = this.formEl.querySelector('.url-form__fieldset');
        this.inputEl = this.formEl.querySelector('.url-form__input');
        this.buttonEl = this.formEl.querySelector('.url-form__button');
        this.errorEl = this.formEl.querySelector('.url-form__error');

        this.formEl.addEventListener('submit', (e) => this.onFormSubmit(e));
        this.inputEl.addEventListener('input', () => this.validate());
        this.inputEl.addEventListener('change', () => this.validate());
        this.inputEl.addEventListener('focus', () => this.validate());
        this.inputEl.addEventListener('blur', () => this.validate());
        this.inputEl.addEventListener('paste', () => this.validate());

        this.setValidState(false);
        this.setSubmitting(false);
        this.setError(null);
        this.achievements.applyData(null);
        this.restoreState();
    }

    onFormSubmit (e) {
        e.preventDefault();

        if (this.isSubmitting) {
            return;
        }

        this.validate();

        if (!this.isValid) {
            return;
        }

        this.setSubmitting(true);
        this.setError(null);        
        this.achievements.applyData(null);
        this.saveState();

        fetch('/achievements', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: this.getURL()
            })
        }).then((response) => {
            return response.json();
        }).then((response) => {
            if (response.isOk) {
                return response.data;
            }

            this.setError(response.error);

            return null;
        }).catch((e) => { 
            console.warn('Failed to send request:', e);

            this.setError('An error occurred while sending request');

            return null;
        }).then((data) => {
            this.setSubmitting(false);
            this.achievements.applyData(data);
            
            console.log(data);
        }); 
    }

    getURL () {
        return (this.inputEl.value || '').trim();
    }

    validate () {
        const url = this.getURL();
        // const isURLValid = isNumeric(url) || url.length >= 6;
        const isURLValid = url.length > 0;

        this.setValidState(isURLValid);
    }

    setValidState (isValid) {
        this.isValid = isValid;
        this.buttonEl.disabled = !this.isValid;
    }

    setSubmitting (isSubmitting) {
        this.isSubmitting = isSubmitting;
        this.fieldsetEl.disabled = this.isSubmitting;
    }

    setError (message) {
        if (message) { 
            this.errorEl.innerHTML = message;
            this.errorEl.hidden = false;
        } else {
            this.errorEl.innerHTML = '';
            this.errorEl.hidden = true;
        }
    }

    saveState () {
        const state = {
            achieved: this.achievements.filterAchieveEl.value,
            orderBy: this.achievements.filterSortEl.value,
            order: this.achievements.filterSortEl.dataset.order,
            url: this.getURL(),
        };

        window.localStorage.setItem('state', JSON.stringify(state));
    }

    restoreState () {
        const defaultState = {
            achieved: 'all',
            orderBy: 'id',
            order: '1',
            url: '',
        };

        let state;

        try {
            state = JSON.parse(window.localStorage.getItem('state')) || defaultState;
        } catch (e) {
            state = defaultState;
        }

        console.log(state);
        
        this.achievements.filterAchieveEl.value = state.achieved;
        this.achievements.filterSortEl.value = state.orderBy;
        this.achievements.filterSortEl.dataset.order = state.order;
        this.inputEl.value = state.url;

        const order = this.achievements.filterSortEl.dataset.order;

        this.achievements.filterSortButtonEls.forEach((btnEl) => {
            if (order === btnEl.dataset.order) {
                btnEl.classList.remove('btn-outline-secondary');
                btnEl.classList.add('btn-secondary');
            }
        });
    }
}


const init = () => {
    const urlForm = new URLForm();
};



/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
