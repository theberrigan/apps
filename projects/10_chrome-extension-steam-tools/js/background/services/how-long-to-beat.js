import { USER_AGENT } from '../common.js';
import { executeOffscreen } from '../offscreen.js';



const DEFAULT_SEARCH_INFO = {
    endpoint: null,
    key: null,
};

const SEARCH_KEY_CACHE_KEY = 'searchKey';
const SEARCH_KEY_CACHE_DURATION = 12 * 60 * 60;  // sec



export class HowLongToBeat {
    // https://developer.chrome.com/docs/extensions/reference/storage/#type-StorageArea
    getFromStorage = async (key, defaultValue = null) => {
        const result = await chrome.storage.local.get(key);
        const data   = result[key];

        if (data === undefined) {
            return defaultValue;
        }

        const { value, timeout } = data;

        if (timeout === null) {
            return value;
        }

        if (Date.now() >= timeout) {
            await chrome.storage.local.remove(key);

            return defaultValue;
        }

        return value;
    }

    setToStorage = async (key, value, timeout = null) => {
        if (Number.isFinite(timeout)) {
            timeout = Date.now() + timeout * 1000 
        } else {
            timeout = null;
        }

        await chrome.storage.local.set({
            [ key ]: {
                value,
                timeout
            }
        });
    }

    fetchSearchKey = async (forceUpdate = false) => {
        if (!forceUpdate) {
            const searchInfo = await this.getFromStorage(SEARCH_KEY_CACHE_KEY);

            if (searchInfo !== null) {
                console.log('Get search key from cache:', searchInfo);
                return searchInfo;
            }            
        }

        let response = await fetch('https://howlongtobeat.com', {
            method: 'GET'
        }).then((response) => {
            return response.text();
        }).catch((error) => {
            console.error('Failed to fetch:', error);
            return null;
        });

        if (!response) {
            console.error('Failed to fetch search key');        
            return DEFAULT_SEARCH_INFO;
        }

        let match = response.match(/src="([^"]+_app\-[\da-f]+\.js)"/i);

        if (!match) {
            console.error('Failed to fetch search key');        
            return DEFAULT_SEARCH_INFO;
        }

        const url = new URL(match[1], 'https://howlongtobeat.com');
        
        response = await fetch(url, {
            method: 'GET'
        }).then((response) => {
            return response.text();
        }).catch((error) => {
            console.error('Failed to fetch:', error);
            return null;
        });

        if (!response) {
            console.error('Failed to fetch search key');        
            return DEFAULT_SEARCH_INFO;
        }

        // fetch("/api/s/".concat("7a605043").concat("81a39f40")
        match = response.match(/fetch\("\/api\/([^\/]+)\/"\.concat\("([^"]+)"\)\.concat\("([^"]+)"\)/i);

        if (!match) {
            console.error('Failed to fetch search key');        
            return DEFAULT_SEARCH_INFO;
        }

        const searchInfo = {
            endpoint: match[1],
            key: match[2] + match[3]
        };

        await this.setToStorage(SEARCH_KEY_CACHE_KEY, searchInfo);

        console.log('Search key has been cached:', searchInfo);

        return searchInfo;
    }

    extractConfig = async (html) => {
        return executeOffscreen('HLTB_EXTRACT_CONFIG', {
            html        
        });
    }

    fetchGameData = async (appId, appName) => {
        // const searchTerms = appName.split(/[\r\s\t\n!#%&":;,\-\?\<\>\.\*\(\)\{\}\[\]\|]+/g);
        const searchTerms = appName.split(/[^\p{L}\d']+/u).filter(c => c);

        const searchData = {
            searchType: 'games',
            searchTerms,
            searchPage: 1,
            size: 20,
            searchOptions: {
                games: {
                    userId: 0, 
                    platform: '', 
                    sortCategory: 'popular', 
                    rangeCategory: 'main', 
                    rangeTime: {
                        min: null, 
                        max: null
                    }, 
                    gameplay: {
                        perspective: '', 
                        flow: '', 
                        genre: '',
                        difficulty: ''
                    }, 
                    rangeYear: {
                        min: '', 
                        max: ''
                    }, 
                    modifier: ''
                }, 
                users: {
                    sortCategory: 'postcount'
                }, 
                lists: {
                    sortCategory: 'follows'
                }, 
                filter: '', 
                sort: 0, 
                randomizer: 0
            },
            useCache: true,
        };

        let games = [];

        for (let isRetry of [ false, true ]) { 
            const { endpoint, key } = await this.fetchSearchKey(isRetry);

            if (!endpoint || !key) {
                continue;
            }

            const url = `https://howlongtobeat.com/api/${ endpoint }/${ key }`;

            const response = await fetch(url, {
                method: 'POST',
                body: JSON.stringify(searchData),
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }).then((response) => {
                return response.text();
            }).catch((error) => {
                console.error('Failed to fetch:', error);
                return null;
            });

            if (!response) {
                return null;
            }

            try {
                games = JSON.parse(response).data;
                break;
            } catch (e) {}
        }

        if (!games) {
            return null;
        }

        let app = null;

        for (let game of games) {
            const html = await fetch(`https://howlongtobeat.com/game/${ game.game_id }`, {
                method: 'GET'
            }).then((response) => {
                return response.text();
            }).catch((error) => {
                console.error('Failed to fetch:', error);
                return null;
            });

            const config = await this.extractConfig(html);

            if (config) {
                const games = JSON.parse(config).props?.pageProps?.game?.data?.game;

                if (games) {
                    app = games.find(a => a.profile_steam === appId);
                }

                if (app) {
                    break;
                }
            }
        }

        if (!app) {
            return null;
        }

        return {
            id: app.game_id,
            name: app.game_name,
            steamAppId: app.profile_steam,
            time: {
                main: app.comp_main,  // Main Story
                plus: app.comp_plus,  // Main + Extras
                full: app.comp_100    // Completionist
            }
        };
    }
}
