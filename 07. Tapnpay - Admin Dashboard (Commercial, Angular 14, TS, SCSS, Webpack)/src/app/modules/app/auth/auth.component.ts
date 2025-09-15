import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {FormBuilder} from '@angular/forms';
import {Subscription} from 'rxjs';
import {UserService} from '../../../services/user.service';

type Mode = null | 'welcome' | 'redirect' | 'error';

@Component({
    selector: 'auth',
    templateUrl: './auth.component.html',
    styleUrls: [ './auth.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auth'
    },
})
export class AuthComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    mode : Mode = null;

    isSubmitting : boolean = false;

    errorMessage : string;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private userService : UserService,
    ) {
        window.scroll(0, 0);
        this.titleService.setTitle('auth.page_title');
    }

    ngOnInit () : void {
        const code : string = this.route.snapshot.queryParams['code'] || null;

        if (code) {
            this.mode = 'redirect';
            this.userService.auth(code).then((isOk : boolean) => {
                if (isOk) {
                    this.router.navigateByUrl('/dashboard');
                } else {
                    this.errorMessage = 'auth.error_common';
                    this.mode = 'error';
                }
            });
        } else {
            this.mode = 'welcome';
        }
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onAuthClick () {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        this.userService.fetchAuthUrl().then((url : string) => {
            if (url) {
                // https://tnp-console-dev.eu.ngrok.io/auth?code=c073d1d6-54ec-437e-8dcd-d50d8073e5b5
                window.location.assign('//' + url);
            } else {
                this.isSubmitting = false;
                this.errorMessage = 'auth.error_common';
                this.mode = 'error';
            }
        });
    }
}

