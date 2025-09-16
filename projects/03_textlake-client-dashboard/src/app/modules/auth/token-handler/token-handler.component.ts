import {Component, EventEmitter, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {UserService} from '../../../services/user.service';
// import {UserService} from '../../../services/user.service';
// import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'token-handler',
    templateUrl: './token-handler.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auth__redirect-message'
    }
})
export class TokenHandlerComponent implements OnInit {
    @Output()
    public onAfterSignIn = new EventEmitter<void>();

    constructor (
        private router : Router,
        private userService : UserService,
        // private titleService : TitleService
    ) {
        // this.titleService.setTitle('auth.social_auth.page_title');
    }

    public ngOnInit () : void {
        /*
        this.userService
            .exchangeCodeForToken()
            .then((result : any) => {
                switch (result.action) {
                    case 'COMPLETE':
                        this.onAfterSignIn.emit();
                        break;
                    case 'ERROR':
                        this.userService.setRouterData('sign-in', {
                            message: {
                                type: 'error',
                                messageKey: result.error,
                                messageData: result.errorData
                            }
                        });
                        this.router.navigateByUrl('/auth/sign-in');
                        break;
                    case 'PLAN':
                        this.router.navigateByUrl('/dashboard/plan');
                        break;
                    default:
                        console.warn('Unexpected behavior');
                }
            });*/
    }
}
