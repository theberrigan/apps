import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {
    userRegistrationFlowType,
    UserRegistrationFlowTypeService
} from "../../../services/user-registration-flow-type.service";
import {UserService} from "../../../services/user.service";

@Component({
    selector: 'app-profile-nav',
    templateUrl: './profile-nav.component.html',
    styleUrls: ['./profile-nav.component.scss'],
})
export class ProfileNavComponent implements OnInit {

    @Input() isDebtLock: boolean;
    public isShowSubscription: boolean;
    @Output() OnShowPaymentMethodPopup = new EventEmitter();
    @Output() OnDeactivateAccount = new EventEmitter();

    public isLoaded: boolean = false;
    isShowAutoPayments: boolean = true;

    constructor(private flowTypeService: UserRegistrationFlowTypeService,
                private userService: UserService) {
    }

    ngOnInit(): void {
        this.flowTypeService.getFlowType().then((flowType: userRegistrationFlowType) => {
            this.isShowSubscription = flowType === userRegistrationFlowType.PAY_PER_BUNDLE;
            this.isLoaded = true;
        })
    }

    public emmitShowPaymentMethodPopup(): void {
        this.OnShowPaymentMethodPopup.emit();
    }

    public emmitDeactivateAccount(): void {
        this.OnDeactivateAccount.emit();
    }

    isShowDeactivateAccountBtn() {
        return this.userService.getUserData().account.tollAuthority === 'NTTA';
    }
}
