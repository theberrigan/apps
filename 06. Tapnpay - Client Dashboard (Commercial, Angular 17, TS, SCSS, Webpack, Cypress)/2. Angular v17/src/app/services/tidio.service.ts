import { Injectable } from '@angular/core';
import { CONFIG } from '../../../config/app/dev';

@Injectable({
    providedIn: 'root'
})
export class TidioService {
    private promise : Promise<any> = null;

    private isVisible : boolean = false;

    constructor () {}

    async changeVisibility (isVisible : boolean) {
        this.isVisible = isVisible;

        // TIDIO is disabled by request

        // const tidioInstance = await this.getInstance();
        //
        // if (tidioInstance) {
        //     tidioInstance.display(this.isVisible);
        // }
    }

    async getInstance () : Promise<any> {
        if (!this.promise) {
            this.promise = new Promise((resolve) => {
                const script : any = document.createElement('script');

                script.addEventListener('error', () => resolve(null));

                script.src = `//code.tidio.co/${ CONFIG.tidio.apiKey }.js`;
                document.body.appendChild(script);

                const onReady = () => {
                    const tidioInstance = (<any>window).tidioChatApi;

                    tidioInstance.display(this.isVisible);
                    tidioInstance.setFeatures({ mobileHash: false });

                    resolve(tidioInstance);
                };

                if ((<any>window).tidioChatApi) {
                    (<any>window).tidioChatApi.on('ready', onReady);
                } else {
                    document.addEventListener('tidioChat-ready', onReady);
                }
            });
        }

        return this.promise;
    }
}
