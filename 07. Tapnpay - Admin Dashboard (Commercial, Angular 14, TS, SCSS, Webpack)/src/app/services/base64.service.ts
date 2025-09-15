import { Injectable } from '@angular/core';
// import * as base64js from 'base64-js';

@Injectable({
    providedIn: 'root'
})
export class Base64Service {
    constructor () {}

    /*
    encode (str) : string {
        const bytes = new TextEncoder().encode(str);
        return base64js.fromByteArray(bytes);
    }

    decode (str) : string {
        const bytes = base64js.toByteArray(str);
        return new TextDecoder().decode(bytes);
    }
    */

    /*
    encode (str) : string {
        const bytes = encodeURIComponent(str).replace(/%([\dA-F]{2})/g, (_, value) => {
            return String.fromCharCode(parseInt(value, 16));
        });

        return btoa(bytes);
    }

    decode (str) : string {
        const chars = atob(str).split('');
        const uriEncoded = chars.map(char => ('%' + char.charCodeAt(0).toString(16).padStart(2, '0'))).join('');

        return decodeURIComponent(uriEncoded);
    }
    */

    encode (str) : string {
        const bytes = [ ...new TextEncoder().encode(str) ];
        const binary = bytes.map(byte => String.fromCharCode(byte)).join('');

        return btoa(binary);
    }

    decode (str) : string {
        const chars = atob(str).split('');
        const bytes = new Uint8Array(chars.map(char => char.charCodeAt(0)));

        return new TextDecoder().decode(bytes);
    }
}
