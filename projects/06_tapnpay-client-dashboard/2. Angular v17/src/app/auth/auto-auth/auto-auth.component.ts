import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {UserService} from '../../services/user.service';
import {MessageService} from '../../services/message.service';

@Component({
    selector: 'auto-auth',
    templateUrl: './auto-auth.component.html',
    styleUrls: ['./auto-auth.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auto-auth'
    },
})
export class AutoAuthComponent implements OnInit, OnDestroy {
    constructor(
        private renderer: Renderer2,
        private router: Router,
        private route: ActivatedRoute,
        private userService: UserService,
        private messageService: MessageService,
    ) {

    }

    ngOnInit(): void {
        const authTokenFromUrl: string | null = this.route.snapshot.params['token'] || null;

        this.validateAuthTokenFromUrl(authTokenFromUrl);
    }

    private validateAuthTokenFromUrl(authTokenFromUrl: string) {
        this.userService.validateToken(authTokenFromUrl).subscribe(
            (isTokenValid: boolean) => {
                this.onAfterTokenValidate(isTokenValid, authTokenFromUrl)
            },
            (_err) => {
                this.onAfterTokenValidate(false, authTokenFromUrl)
            }
        );
    }

    ngOnDestroy(): void {

    }

    onAfterTokenValidate(isTokenValid: boolean, token: string) {
        if (!isTokenValid) {
            return this.onInvalidToken();
        }

        this.userService.applyToken(token, false).then(isTokenApplyForUser => {
            if (!isTokenApplyForUser) {
                return this.onInvalidToken();
            }

            this.router.navigateByUrl('/dashboard/invoices');
        });
    }

    onInvalidToken() {
        const urlMessage = this.messageService.encodeUrlMessage({
            key: 'auth.invalid_auth_token'
        });

        this.router.navigateByUrl(`/auth?authError=${urlMessage}`);
    }
}

