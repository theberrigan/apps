import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class Base64Service {
    constructor () {}

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
