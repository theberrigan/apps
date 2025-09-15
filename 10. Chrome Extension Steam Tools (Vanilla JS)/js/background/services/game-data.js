import { SteamHunters } from './steam-hunters.js';
import { HowLongToBeat } from './how-long-to-beat.js';



export const fetchGameData = async ({ appId, appName }) => {
    const hltb = new HowLongToBeat();
    const sh   = new SteamHunters();

    let response = await Promise.all([
        hltb.fetchGameData(appId, appName),
        sh.fetchGameData(appId)
    ]).catch((e) => {
        console.log('Failed to fetch data:', e);
        return [ null, null ];
    });

    return {
        hltb: response[0],
        steamHunters: response[1],
    };
};