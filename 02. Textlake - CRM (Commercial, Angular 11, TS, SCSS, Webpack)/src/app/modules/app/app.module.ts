import { BrowserModule } from '@angular/platform-browser';
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClient, HttpClientModule } from '@angular/common/http';

import {TranslateModule, TranslateLoader} from '@ngx-translate/core';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent }     from './app.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { SharedModule } from '../shared.module';
import {UserService} from '../../services/user.service';
import {DEFAULT_LANG, LangService} from '../../services/lang.service';
import {ApiRequestInterceptor} from '../../interceptors/api-request-interceptor';
import { CONFIG } from '../../../../config/app/dev';
import {PopupComponent} from '../../widgets/popup/popup.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {DatetimeService} from '../../services/datetime.service';
import {Observable} from 'rxjs';

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

export function initApp (
    userService : UserService,
    langService : LangService
) {
    return () : Promise<any> => {
        return new Promise((resolve) => {
            langService.setDefaultLang(DEFAULT_LANG.code);
            userService.restoreUser().then(() => resolve());
        });
    }
}

@NgModule({
    declarations: [
        AppComponent,
        NotFoundComponent
    ],
    imports: [
        BrowserAnimationsModule,
        // BrowserModule,
        SharedModule,
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
            provide: HTTP_INTERCEPTORS,
            useClass: ApiRequestInterceptor,
            multi: true
        },
        {
            provide: APP_INITIALIZER,
            useFactory: initApp,
            deps: [
                UserService,
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
