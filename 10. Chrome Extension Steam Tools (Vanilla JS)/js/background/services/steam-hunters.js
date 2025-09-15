import { executeOffscreen } from '../offscreen.js';



export class SteamHunters {
    fetchGamePage = async (appId) => {
        const html = await fetch(`https://steamhunters.com/apps/${ appId }/achievements`, {
            method: 'GET'
        }).then((response) => {
            return response.text();
        }).catch((error) => {
            console.error('Failed to fetch:', error);
            return null;
        });

        return html;
    }

    extractAPIToken = async (html) => {
        return executeOffscreen('SH_EXTRACT_API_TOKEN', {
            html
        });
    }

    extractGameData = async (html) => {
        return executeOffscreen('SH_EXTRACT_GAME_DATA', {
            html
        });
    }

    extractFullGameData = async (html) => {
        return executeOffscreen('SH_EXTRACT_FULL_GAME_DATA', {
            html
        });
    }

    fetchGameDataByAPI = async (appId, token) => {
        // medianTime,
        // hasPaidDLC,
        const response = await fetch(`https://steamhunters.com/api/apps/${ appId }`, {
            method: 'GET',
            mode: 'cors',
            credentials: 'include',
            referrer: `https://steamhunters.com/apps/${ appId }/achievements`,
            headers: {
                '__RequestVerificationToken': token,
                'Accept': 'application/json; IEEE754Compatible=true',
            },
        }).then((response) => {
            return response.json();
        }).catch((error) => {
            console.error('Failed to fetch:', error);
            return null;
        });

        if (response && response.appId === appId && typeof response.hasPaidDlc === 'boolean' && typeof response.medianCompletionTime === 'number') {
            return {
                medianTime: response.medianCompletionTime * 60,  // to seconds
                hasPaidDLC: response.hasPaidDlc,
            };
        }

        return null;
    }

    fetchGameData = async (appId) => {
        const html = await this.fetchGamePage(appId);

        if (!html) {
            return null;
        }

        const token = await this.extractAPIToken(html);

        let gameData = null;  // console.log(await this.extractFullGameData(html));

        if (token) {
            gameData = await this.fetchGameDataByAPI(appId, token);
        }

        if (!gameData) {
            gameData = await this.extractGameData(html);
        }

        // if (Number.isFinite(gameData?.medianTime)) {
        //     gameData.medianTime *= 60;  // to seconds
        // }

        return gameData;
    }
}