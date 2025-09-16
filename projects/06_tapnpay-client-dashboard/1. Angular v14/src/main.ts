import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/modules/app/app.module';
import { CONFIG } from '../config/app/dev';

if (CONFIG.isProduction) {
    console.log(`%c Tapnpay Client Dashboard v${ APP_VERSION } built on ${ APP_RELEASE_DATE } `, 'background: #5B7CD2; color: #fff; font-weight: bold;');
    enableProdMode();
}

platformBrowserDynamic()
    .bootstrapModule(AppModule)
    .catch(err => console.error(err));
