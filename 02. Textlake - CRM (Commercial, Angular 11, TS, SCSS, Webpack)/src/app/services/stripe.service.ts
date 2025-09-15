import { Injectable }       from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {CONFIG} from '../../../config/app/dev';

@Injectable({
    providedIn: 'root'
})
export class StripeService {
    public instances : any = {};

    public stripe : any = null;

    public supportedLocales : string[] = [
        'no', 'nl', 'pl', 'sv', 'zh',
        'fi', 'fr', 'he', 'it', 'ja',
        'ar', 'da', 'de', 'en', 'es',
    ];

    constructor (
        public translate : TranslateService
    ) {
        this.stripe = new Promise((resolve) => {
            const script : any = document.createElement('script');

            script.addEventListener('load', () => resolve((<any>window).Stripe));
            script.addEventListener('error', () => resolve(null));

            script.src = 'https://js.stripe.com/v3/';

            document.head.appendChild(script);
        });
    }

    public getInstance (apiKey : string = null) {
        return new Promise((resolve) => {
            apiKey = apiKey || CONFIG.payments.stripe.apiKey;

            this.stripe.then((Stripe : any) => {
                if (apiKey in this.instances) {
                    resolve(this.instances[apiKey]);
                } else {
                    resolve(this.instances[apiKey] = Stripe(apiKey));
                }
            });
        });
    }

    public getLocale () : string {
        const currentLang : string = this.translate.currentLang;
        return this.supportedLocales.indexOf(currentLang) > -1 ? currentLang : 'auto';
    }
}
