import {Component, Input, OnInit} from '@angular/core';
import {PendingLPN} from "../../../../services/license-plates.service";
import {animate, style, transition, trigger} from "@angular/animations";
import {AbstractControl, ControlContainer, FormGroup, UntypedFormGroup, ValidatorFn, Validators} from "@angular/forms";
import {FormValidationService} from "../../../../_shared/validation-message/form-validation.service";
import {UserService} from "../../../../services/user.service";
import {
    LicensePlateCategory
} from "../_interfaces/license-plate-categories-http-response";
import {
    maxDateValidator,
    minDateTodayValidator,
    minOneHourDurationValidator,
} from "../../../../_shared/validators/date-validator";

const startAnimationStyles = {height: '100px', opacity: 1};
const endBlockStyles = {height: 0, opacity: 0};
const inOutAnimationDuration: string = '0.3s';

const enterAnimationType = ' ease-out';
const outAnimationType = ' ease-in';

@Component({
    selector: 'app-lpn-card',
    templateUrl: './lpn-card.component.html',
    styleUrls: ['./lpn-card.component.scss'],
    animations: [
        trigger(
            'inOutAnimation',
            [
                transition(
                    ':enter',
                    [
                        style(endBlockStyles),
                        animate(inOutAnimationDuration + enterAnimationType,
                            style(startAnimationStyles))
                    ]
                ),
                transition(
                    ':leave',
                    [
                        style(startAnimationStyles),
                        animate(inOutAnimationDuration + outAnimationType,
                            style(endBlockStyles))
                    ]
                )
            ]
        )
    ],
})
export class LpnCardComponent implements OnInit {

    @Input() pendingLPNsFee;
    @Input() plate: PendingLPN;
    @Input() isDisabledToSelect: boolean = false;

    @Input() selectModel;
    @Input() datesModel;
    @Input() form: FormGroup;
    @Input() maxDateForRentalCarPeriod: Date;
    @Input() maxDurationInDaysForRentalCarPeriod: number = 0;
    vehicleType: 'rental' | 'personal' = 'personal';
    lpnTypes = '';
    userTollAuthority = this.userService.userData.account.tollAuthority;

    mainFromGroup: UntypedFormGroup;

    @Input() listOfLPNTypesIPASS: LicensePlateCategory[] = [];
    listOfLPNTypes: {} = null;
    public readonly _rentalTypeName = 'RENTAL';

    constructor(private formValidatorService: FormValidationService,
                private userService: UserService,
                private controlContainer: ControlContainer) {

    }

    ngOnInit(): void {
        this.listOfLPNTypes = this.createLPNTypeList(this.plate);
        this.mainFromGroup = this.controlContainer.control as UntypedFormGroup;

        if (this.plate.rental) {
            this.setRentalPeriodValidators();
        }

        this.mainFromGroup.get('lpn_type').valueChanges.subscribe((value) => {
            if (value === this._rentalTypeName) {
                this.setRentalPeriodValidators();
            } else {
                this.deleteRentalPeriodValidators();
            }
        });

        this.mainFromGroup.get('is_selected_to_pay').valueChanges.subscribe(
            (value) => {
                if (!value) {
                    this.deleteRentalPeriodValidators();
                }
            }
        )
    }

    private createLPNTypeList(plate: PendingLPN) {
        const cat = plate.supported_types;
        return cat.reduce((obj, id) => {
            obj[id] = {
                name: id.charAt(0) + id.slice(1).toLowerCase(),
                translate_key: id.toLowerCase()
            };
            return obj;
        }, {});
    }

    public getField(controlName: string, parentFormGroupName: string): AbstractControl {
        const parentFormGroup = this.mainFromGroup.get(parentFormGroupName) as UntypedFormGroup;
        return this.formValidatorService.getFormControl(controlName, parentFormGroup);
    }

    isLpnSupportRentalType(lpn: PendingLPN): boolean {
        const lpnSupportedTypes = lpn.supported_types;
        const rentalTypeName = this._rentalTypeName;
        return lpn && lpnSupportedTypes && lpnSupportedTypes.includes(rentalTypeName);
    }

    public isActiveToolAuthority(toolAuthority: string): boolean {
        return toolAuthority === this.userTollAuthority;
    }

    getLPNTypeTranslateKey(value: { name: string, translate_key: string }): string {
        return `dashboard.fleet.vehicle_types.${value.translate_key}`;
    }

    private readonly _endDateControlName = 'endDate';
    private readonly _endTimeControlName = 'endTime';
    private readonly _rentalPeriodFormGroupName = 'rental_period';
    @Input() isShowFee: boolean = true;

    private getRentalPeriodFormControls() {
        const RentalPeriodFromGroup = this.mainFromGroup.get(this._rentalPeriodFormGroupName);
        const endDateControl = RentalPeriodFromGroup.get(this._endDateControlName);
        const endTimeControl = RentalPeriodFromGroup.get(this._endTimeControlName);
        return {RentalPeriodFromGroup, endDateControl, endTimeControl};
    }

    private setRentalPeriodValidators() {
        const {RentalPeriodFromGroup, endDateControl, endTimeControl} = this.getRentalPeriodFormControls();

        const endDateValidators: ValidatorFn = Validators.compose([Validators.required, minDateTodayValidator()]);
        const endTimeValidator = Validators.compose([Validators.required, minOneHourDurationValidator(),]);
        const rentalPeriodValidator = maxDateValidator(this.maxDateForRentalCarPeriod);

        endDateControl.setValidators(endDateValidators);
        endDateControl.updateValueAndValidity();
        endTimeControl.setValidators(endTimeValidator);
        endTimeControl.updateValueAndValidity();
        RentalPeriodFromGroup.setValidators(rentalPeriodValidator);
        RentalPeriodFromGroup.updateValueAndValidity();
    }

    private deleteRentalPeriodValidators() {
        const {RentalPeriodFromGroup, endDateControl, endTimeControl} = this.getRentalPeriodFormControls();

        endDateControl.clearValidators();
        endDateControl.updateValueAndValidity();

        endTimeControl.clearValidators();
        endTimeControl.updateValueAndValidity();

        RentalPeriodFromGroup.clearValidators();
        RentalPeriodFromGroup.updateValueAndValidity();
    }

    getCategoryTranslateKey(name: string): string {
        return `lpn_categories.${name}`
    }
}
