import {Injectable} from '@angular/core';
import {DomSanitizer} from "@angular/platform-browser";

@Injectable({
    providedIn: 'root'
})
export class AsyncJsScriptLoaderService {

    constructor(private DOMSanitizer: DomSanitizer) {

    }

    public loadScript(url: string = 'https://tag.simpli.fi/sifitag/42ddb5b0-ea8b-013a-53cc-0cc47a8ffaac.js', scriptName: string = 'tag manager') {
        console.log('preparing to load...')
        let node: HTMLScriptElement = document.createElement('script');
        node.src = url;
        node.type = 'text/javascript';
        node.async = true;

        const pageHeadHtmlElement: HTMLHeadElement = document.getElementsByTagName('head')[0];
        if (pageHeadHtmlElement) {
            pageHeadHtmlElement.appendChild(node);
        } else {
            console.warn('page head not found');
        }
        console.warn(`script ${scriptName} was loaded`);
    }
}
