import { APP_INITIALIZER, NgModule } from '@angular/core';
import { CommonModule  } from '@angular/common';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule }  from '@angular/router';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import {Observable} from 'rxjs';
import { TranslateModule, TranslateLoader, TranslateService } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { AppComponent }  from './app.component';
import { NotFoundComponent }  from './not-found/not-found.component';
import { AppRoutes }     from './app.routes';
import { SharedModule }  from '../shared.module';
import { UserService }   from '../../services/user.service';
import { HttpService }   from '../../services/http.service';
import { RequestInterceptor } from '../../interceptors/request.interceptor';
import { CyPipe } from '../../pipes/cy.pipe';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {DEFAULT_LANG} from '../../services/lang.service';

export class LocaleHttpLoader implements TranslateLoader {
    private readonly hashes = LOCALES_HASHES;

    constructor (
        private http : HttpClient
    ) {}

    public getTranslation (lang : string) : Observable<Object> {
        const hash = this.hashes[ lang.toLowerCase() ] || encodeURIComponent(new Date().toISOString().match(/^\d+-\d+-\d+/)[0]);
        return this.http.get(`/assets/locale/${ lang }.json?hash=${ hash }`);
    }
}

export function initFactory (
    httpService : HttpService,
    userService : UserService,
    translateService : TranslateService
) : any {
    return () => {
        return new Promise((resolve) => {
            translateService.setDefaultLang(DEFAULT_LANG.code);
            userService.restoreUser().then(() => resolve());
        });
    };
}

@NgModule({
    declarations: [
        AppComponent,
        NotFoundComponent
    ],
    imports: [
        // CommonModule,
        // BrowserModule,
        BrowserAnimationsModule,
        SharedModule,
        HttpClientModule,
        AppRoutes,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: LocaleHttpLoader,
                deps: [ HttpClient ]
            }
        }),
        // FormsModule,
        // ReactiveFormsModule,
    ],
    providers: [
        {
            provide: HTTP_INTERCEPTORS,
            useClass: RequestInterceptor,
            multi: true
        },
        {
            provide: APP_INITIALIZER,
            useFactory: initFactory,
            deps: [
                HttpService,
                UserService,
                TranslateService
            ],
            multi: true
        }
    ],
    bootstrap: [
        AppComponent
    ]
})
export class AppModule {}
