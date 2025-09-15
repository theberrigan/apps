import { Injectable } from '@angular/core';

export interface URLMessageData {
    key : string;
    data? : any;
}

@Injectable({
    providedIn: 'root'
})
export class MessageService {
    constructor () {

    }

    encodeUrlMessage (messageData : URLMessageData) {
        try {
            return encodeURIComponent(window.btoa(JSON.stringify(messageData)));
        } catch (e) {
            console.warn('Failed to encode URL message:', messageData);
            return null;
        }
    }

    decodeUrlMessage (urlMessage : string) : URLMessageData {
        try {
            return JSON.parse(window.atob(decodeURIComponent(urlMessage)));
        } catch (e) {
            console.warn('Failed to decode URL message:', urlMessage);
            return null;
        }
    }

    extractMessageDataFromURL (url : string, paramKey : string) : URLMessageData | null {
        if (typeof url !== 'string' || !url.trim() || typeof paramKey !== 'string' || !paramKey.trim()) {
            return null;
        }

        const queryParamsString : string = url.trim().split('#')[0].split('?')[1];

        if (!queryParamsString) {
            return null;
        }

        const queryParams = {};

        queryParamsString.split(/&/g).forEach(pair => {
            const [ key, value = '' ] = pair.split('=');
            queryParams[ key.trim() ] = value.trim();
        });

        if (!queryParams[paramKey]) {
            return null;
        }

        return this.decodeUrlMessage(queryParams[paramKey]);
    }
}
