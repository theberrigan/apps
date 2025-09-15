import { BrowserModule } from '@angular/platform-browser';
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClient, HttpClientModule } from '@angular/common/http';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Observable} from 'rxjs';

import {TranslateModule, TranslateLoader} from '@ngx-translate/core';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent }     from './app.component';
import { LandingComponent }     from './landing.component';
import { SharedModule } from '../shared.module';
import {DEFAULT_LANG, LangService} from '../../services/lang.service';
import { CONFIG } from '../../../../config/app/dev';
import {FileUploadModule} from 'ng2-file-upload';

export class LocaleHttpLoader implements TranslateLoader {
    private readonly hashes = LOCALES_HASHES;

    constructor (
        private http : HttpClient
    ) {}

    public getTranslation (lang : string) : Observable<Object> {
        const hash = this.hashes[ lang.toLowerCase() ] || encodeURIComponent(APP_VERSION || new Date().toISOString().match(/^\d+-\d+-\d+/)[0]);
        return this.http.get(`/assets/locale/${ lang }.json?hash=${ hash }`);
    }
}

export function initApp (langService : LangService) {
    return () : Promise<any> => {
        return new Promise((resolve) => {
            langService.setDefaultLang(DEFAULT_LANG.code);
            // setTimeout(() => resolve(), 5000);
            resolve();
        });
    }
}

@NgModule({
    declarations: [
        AppComponent,
        LandingComponent
    ],
    imports: [
        BrowserAnimationsModule,
        // BrowserModule,
        SharedModule,
        FileUploadModule,
        HttpClientModule,
        AppRoutingModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: LocaleHttpLoader,
                deps: [ HttpClient ]
            }
        })
    ],
    providers: [
        {
            provide: APP_INITIALIZER,
            useFactory: initApp,
            deps: [
                LangService
            ],
            multi: true
        },
    ],
    bootstrap: [
        AppComponent
    ]
})
export class AppModule {}
