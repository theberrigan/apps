import {Component, EventEmitter, OnInit} from '@angular/core';
import {DialogRef} from "@angular/cdk/dialog";
import {FormBuilder, UntypedFormGroup, Validators} from "@angular/forms";
import {LicensePlatesService, PendingLPN, PendingLPNResponse} from "../../../services/license-plates.service";
import {FormValidationService} from "../../../_shared/validation-message/form-validation.service";
import {
    ConfirmFleetPaymentService,
    EmmitNewPendingLicensePlatesListToPayParams
} from "../../../dashboard/_services/confirm-fleet-payment.service";
import {PendingPlateCreateModel} from "../../../dashboard/dashboard/dashboard.component";
import {UserService} from "../../../services/user.service";
import {forkJoin, Observable, tap, throwError} from "rxjs";
import {catchError, map} from "rxjs/operators";
import {FlowGlobalStateService} from "../../../subscriptions/_services/flow-global-state.service";
import {IsShowAddVehicleModalAfterLoginService} from "../../../services/is-show-add-vehicle-modal-after-login.service";

export interface LPNFromFormValue {
    id: string;
    lps: string;
    lpn: string;
    rental: boolean;
    rental_period: RentalPeriod;
    lpn_type: string;
    is_selected_to_pay: boolean;
    lpn_category: string;
}

export interface RentalPeriod {
    endDate: string;
    endTime: string;
}

export interface FleetLpRegistrationEvent {

}

@Component({
    selector: 'app-fleet-lpn-register',
    templateUrl: './fleet-lpn-register.component.html',
    styleUrls: ['./fleet-lpn-register.component.css']
})
export class FleetLpnRegisterComponent implements OnInit {
    pendingLPNsForm: UntypedFormGroup;

    MAX_DATE_FOR_RENTAL_CAR_PERIOD: Date;
    MAX_DURATION_IN_DAYS_FOR_RENTAL_CAR_PERIOD: number;

    selectedForPaymentPendingLPNsCount: number;
    selectedForPaymentPendingLPNsTotalSum: number;
    private canSubmitOneTimePayment: boolean;

    public isLoading: boolean = true;
    public lpnTypesByLps: unknown;

    add: EventEmitter<FleetLpRegistrationEvent> = new EventEmitter();
    cancel: EventEmitter<FleetLpRegistrationEvent> = new EventEmitter();

    public pendingLPNResponse: PendingLPNResponse;
    public isInProgress: boolean = false; // TODO update component to on/off this property when needed
    public isPayByCarPaymentModel: boolean = false;
    public isPayByBundlePaymentModel: boolean = false;

    constructor(
        private dialogRef: DialogRef<any>,
        private licensePlateService: LicensePlatesService,
        private formValidatorService: FormValidationService,
        private fb: FormBuilder,
        private confirmFleetPaymentService: ConfirmFleetPaymentService,
        private userService: UserService,
        private flowGlobalStateService: FlowGlobalStateService,
        private isShowAddVehicleModalAfterLoginService: IsShowAddVehicleModalAfterLoginService) {
    }

    ngOnInit(): void {

        this.licensePlateService.getPendingLPNs().subscribe((resp) => {
            this.pendingLPNResponse = resp;


            this.isPayByBundlePaymentModel = this.flowGlobalStateService.isPayPerBundle();
            this.isPayByCarPaymentModel = this.flowGlobalStateService.isPayPerCar();

            const tollAuthorityName: string = this.userService.userData.account.tollAuthority;
            this.getListOfLPNTypes({state: 'IL', toll_authority_name: tollAuthorityName}); // TODO why IL is here?????

            this.pendingLPNsForm = this.fb.group({});
            const {max_rental_date, max_rental_days} = this.pendingLPNResponse;

            if (max_rental_date !== this.MAX_DATE_FOR_RENTAL_CAR_PERIOD) {
                this.MAX_DATE_FOR_RENTAL_CAR_PERIOD = max_rental_date;
            }
            if (max_rental_days !== this.MAX_DURATION_IN_DAYS_FOR_RENTAL_CAR_PERIOD) {
                this.MAX_DURATION_IN_DAYS_FOR_RENTAL_CAR_PERIOD = max_rental_days;
            }

            let stateObservables = this.makeListOfLPNsStatesUnique(this.pendingLPNResponse.plates).map(state => {
                return this.getListOfLPNTypes({state, toll_authority_name: tollAuthorityName}).pipe(
                    map(response => ({state, response}))
                );
            });

            forkJoin(stateObservables).subscribe(results => {
                let resultObj = results.reduce((acc, result) => {
                    acc[result.state] = result.response;
                    return acc;
                }, {});
                // Now resultObj is an object with states as keys and responses as values.
                this.lpnTypesByLps = resultObj;
                this.addFormControlsForRentalLPNs();
            });

            this.makeListOfLPNsStatesUnique(this.pendingLPNResponse.plates);
        })
    }

    private addFormControlsForRentalLPNs() {
        this.pendingLPNResponse.plates.forEach((plate) => {
            this.addControlToPendingLPNsForm(plate);
        });
        this.recountTotalSumOfSelectedToPayLPNs();
        this.pendingLPNsForm.valueChanges.subscribe((_value) => {
            this.recountTotalSumOfSelectedToPayLPNs();
        });
    }


    private getListOfLPNTypes(data: { state: string, toll_authority_name: string }): Observable<any> {
        return this.licensePlateService.getListOfLicensePlatesCategories(data).pipe(
            map(
                (response) => {
                    return response.categories
                }
            ),
            catchError((error) => {
                console.error('Error occurred:', error);
                return throwError(error);
            }));
    }

    private makeListOfLPNsStatesUnique(listOfLPNs: PendingLPN[]): string[] {
        const listOfLPNsStates = listOfLPNs.map((lpn) => lpn.lps);
        return [...new Set(listOfLPNsStates)];
    }

    recountTotalSumOfSelectedToPayLPNs(_selectedPlate?: PendingLPN) {
        const formValuesList = Object.values(this.pendingLPNsForm.value);
        if (this.pendingLPNResponse) {
            this.selectedForPaymentPendingLPNsCount = this.getSelectedForPaymentPendingLPNsCount(formValuesList);
            this.selectedForPaymentPendingLPNsTotalSum = this.pendingLPNResponse.fee * this.selectedForPaymentPendingLPNsCount;
        } else {
            this.selectedForPaymentPendingLPNsCount = 0;
            this.selectedForPaymentPendingLPNsTotalSum = 0;
        }

        this.canSubmitOneTimePayment = !!(this.pendingLPNResponse && (this.pendingLPNResponse.fee > 0 || this.selectedForPaymentPendingLPNsCount > 0));
    }

    private getSelectedForPaymentPendingLPNsCount(formValuesList: unknown[]): number {
        return formValuesList.filter((lpnFromList: LPNFromFormValue) => lpnFromList.is_selected_to_pay === true).length;
    }

    getDefaultLPNType(plate: PendingLPN): 'RENTAL' | 'PERSONAL' {
        return plate.rental ? 'RENTAL' : 'PERSONAL';
    }

    private addControlToPendingLPNsForm(plate) {
        this.pendingLPNsForm.addControl(plate.id, this.fb.group(
            {
                id: plate.id,
                lps: plate.lps,
                lpn: plate.lpn,
                rental: plate.rental,
                rental_period: this.fb.group(
                    {
                        endDate: [''],
                        endTime: [''],
                    },
                    {}
                ),
                lpn_type: [this.getDefaultLPNType(this.pendingLPNResponse.plates.find(
                    (plateToFind) => plateToFind.id === plate.id
                )), Validators.required],
                is_selected_to_pay: [true, Validators.required],
                lpn_category: [this.lpnTypesByLps[plate.lps][0].name, Validators.required],
            },
        ),);


        this.isLoading = false;
    }


    onConfirmPendingPLNsToPay() {
        if (this.pendingLPNsForm.valid) {
            this.confirmFleetPaymentService.emmitNewPendingLicensePlatesListToPay(this.createListOfPendingLPNsToPay());
        } else {
            this.formValidatorService.validateFormGroup(this.pendingLPNsForm);
        }
    }

    private createListOfPendingLPNsToPay(): EmmitNewPendingLicensePlatesListToPayParams {
        const listOfSelectedLPNs: PendingPlateCreateModel[] = [];
        const lpnNames: string[] = [];

        for (let plateID in this.pendingLPNsForm.value) {
            const plate = this.pendingLPNsForm.value[plateID];

            if (plate.is_selected_to_pay) {
                this.addLPNToSelectedList(listOfSelectedLPNs, plateID, plate);
                this.addLPNNameToSelectedList(lpnNames, plate);
            }
        }
        return {listOfLPns: listOfSelectedLPNs, lpnNames};

    }

    private addLPNNameToSelectedList(lpnNames: string[], plate) {
        lpnNames.push(plate.lps + ' ' + plate.lpn);
    }

    private addLPNToSelectedList(listOfSelectedLPNs: PendingPlateCreateModel[], plateID: string, plate) {
        listOfSelectedLPNs.push(
            {
                pending_license_plate_id: plateID,
                end_date: plate.lpn_type === 'RENTAL' ? this.confirmFleetPaymentService.getEndDateForRentalLPN(plate, this.pendingLPNsForm.value[plateID]) : null,
                license_plate_type: plate.lpn_type,
                license_plate_category: plate.lpn_category,
            });
    }

    onCancel() {
        // submit an empty list to mark pending LPs as canceled
        this.licensePlateService.acceptPendingLPNsWithRental([])
            .subscribe((data) => {
                this.dialogRef.close();
                this.isShowAddVehicleModalAfterLoginService.isShow() ? this.isShowAddVehicleModalAfterLoginService.hide() : this.cancel.emit(this.emptyEvent)
            });
    }

    onSubmitPayPerBundleMode() {
        if (this.pendingLPNsForm.valid) {
            const LPs: PendingPlateCreateModel[] = this.createListOfPendingLPNsToPay().listOfLPns;
            this.licensePlateService.acceptPendingLPNsWithRental(LPs).subscribe((data) => {
                console.log("PayPerBundle pending LP onSubmit()")
                this.dialogRef.close();
                this.add.emit(this.emptyEvent);
            });
        } else {
            this.formValidatorService.validateFormGroup(this.pendingLPNsForm);
        }
    }

    private emptyEvent: FleetLpRegistrationEvent = {}
}
