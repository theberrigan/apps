import { NgModule }      from '@angular/core';

import { AuthComponent } from './auth.component';
import {SignUpComponent} from './sign-up/sign-up.component';
import {SignInComponent} from './sign-in/sign-in.component';
import {AuthRoutingModule} from './auth-routing.module';
import {SharedModule} from '../shared.module';
import {AuthInputDirective} from '../../directives/auth-input.directive';
import {ForgotPasswordComponent} from './forgot-password/forgot-password.component';
import {ResetPasswordComponent} from './reset-password/reset-password.component';
import {NewPasswordComponent} from './new-password/new-password.component';
import {AuthMessageComponent} from './auth-message/auth-message.component';
import {TokenHandlerComponent} from './token-handler/token-handler.component';
import {PasswordRequirementsComponent} from './password-requirements/password-requirements.component';

@NgModule({
    imports: [
        SharedModule,
        AuthRoutingModule
    ],
    exports: [],
    declarations: [
        AuthComponent,
        SignUpComponent,
        SignInComponent,
        NewPasswordComponent,
        ForgotPasswordComponent,
        ResetPasswordComponent,
        AuthMessageComponent,
        TokenHandlerComponent,
        PasswordRequirementsComponent,
        AuthInputDirective
    ],
    providers: []
})
export class AuthModule {

}
