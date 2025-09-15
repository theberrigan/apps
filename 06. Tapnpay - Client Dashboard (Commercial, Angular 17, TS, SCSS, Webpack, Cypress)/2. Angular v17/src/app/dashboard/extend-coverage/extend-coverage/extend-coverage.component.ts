import {Component, OnInit, ViewEncapsulation} from '@angular/core';
import {ExtendCoverageHttpResponse, ExtendCoverageService} from "../extend-coverage.service";
import {UntypedFormBuilder, UntypedFormGroup} from "@angular/forms";
import {Router} from "@angular/router";
import {ToastService} from "../../../services/toast.service";
import {DeviceService, ViewportBreakpoint} from "../../../services/device.service";
import {Subject, Subscription, takeUntil} from "rxjs";
import {CoverageMatrixHttpResponse} from "./coverage-matrix/coverage-matrix.component";
import {userRegistrationFlowType, UserRegistrationFlowTypeService} from "../../../services/user-registration-flow-type.service";

@Component({
    selector: 'app-extend-coverage',
    templateUrl: './extend-coverage.component.html',
    styleUrls: ['./extend-coverage.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class ExtendCoverageComponent implements OnInit {
    activeModal = false;
    activeList = null;
    extendList = null;
    coverageMatrixData = null;
    controlsMapForm: UntypedFormGroup = null;
    public selectedNamesForExtend: string[] = [];
    isPageLoad = true;
    activeTermsName: string = null;

    subs$: Subscription[] = [];
    private viewportBreakpoint: ViewportBreakpoint;
    public isShowExtendCoverageOption: boolean = false;
    private destroy$ = new Subject<void>();

    constructor(private extendCoverageService: ExtendCoverageService,
                private fb: UntypedFormBuilder,
                private router: Router,
                private toastService: ToastService,
                private deviceViewportService: DeviceService,
                private flowTypeService: UserRegistrationFlowTypeService) {
        this.viewportBreakpoint = this.deviceViewportService.viewportBreakpoint;

        this.subs$.push(this.deviceViewportService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceViewportService.viewportBreakpoint;
            }
        }));
    }

    ngOnInit(): void {
        this.getPageData();
        this.initForm();
        this.initFormValueChangesWatcher();

        /*
        * show extend coverage option only for users without subscription
        * because users with subscription have full coverage
        * */
        this.flowTypeService.getFlowType().then((flowType: userRegistrationFlowType) => {
            this.isShowExtendCoverageOption = flowType !== userRegistrationFlowType.PAY_PER_BUNDLE;
        })

    }

    ngOnDestroy(): void {
        this.subs$.forEach(sub => sub.unsubscribe());
        this.destroy$.next();
        this.destroy$.complete();
    }

    private initFormValueChangesWatcher(): void {
        this.controlsMapForm.valueChanges.pipe(
            takeUntil(this.destroy$)
        ).subscribe(values => {
            this.selectedNamesForExtend = Object.keys(values).filter(key => values[key]);
        });
    }

    private getPageData() {
        this.getExtendCoverageMapping();
        this.getForExtend();
    }

    private getForExtend(): void {
        this.extendCoverageService.getListOfExtendableCoverages().pipe(
            takeUntil(this.destroy$)
        ).subscribe(
            (res: ExtendCoverageHttpResponse) => {
                this.extendList = res.coverage;
                this.buildFormControlsMap(this.extendList);
                this.isPageLoad = false;
            },
            error => {
                console.error('Error fetching extendable coverages:', error);
                this.isPageLoad = false;
            }
        );
    }

    private getExtendCoverageMapping(): void {
        this.extendCoverageService.getExtendCoverageMapping().pipe(
            takeUntil(this.destroy$)
        ).subscribe(
            (res: CoverageMatrixHttpResponse) => {
                this.coverageMatrixData = res.license_plates;
            },
            error => {
                console.error('Error fetching extend coverage mapping:', error);
                // Handle the error appropriately
            }
        );
    }

    public openTermsModal(nameOfTerms: string = ''): void {
        this.activeTermsName = nameOfTerms;
        this.activeModal = !this.activeModal;
    }

    public closeTermsModal(): void {
        this.activeModal = false;
        this.activeTermsName = '';
    }


    public extendCoverage() {
        this.isPageLoad = true;
        const selectedList = this.selectedNamesForExtend;
        this.extendCoverageService.extendCoverage(selectedList).subscribe(
            _res => {
                this.showSussesMessage();
                this.selectedNamesForExtend = [];
                this.controlsMapForm.reset();
                this.coverageMatrixData = null;
                // add delay for this response 1 sec
                setTimeout(() => {
                    this.getPageData();
                }, 3000)
            },
            _err => {
                this.showErrorMessage();
            }
        );
    }


    private initForm() {
        this.controlsMapForm = this.fb.group({});
    }

    private buildFormControlsMap(list) {
        list.forEach(item => this.addControlToFormArray(item.toll_authority_name, false));
    }

    private addControlToFormArray(name: string, _value = false) {
        this.controlsMapForm.addControl(name, this.fb.control(false));
    }


    private showSussesMessage(_messageKey: string = '') {
        this.toastService.create(
            {
                message: ['extend_coverage.success_message'],
                timeout: 700,
                type: "success"
            }
        )
    }

    private showErrorMessage(_messageKey: string = '') {
        this.toastService.create(
            {
                message: ['extend_coverage.error_message'],
                timeout: 700,
                type: "error"
            })
    }

    cancel() {
        this.router.navigate(['/dashboard']);
    }

    public isViewPortDesktop() {
        return this.checkViewPortMode('desktop');
    }

    public isViewPortMobile() {
        return this.checkViewPortMode('mobile');
    }

    public isViewPortTablet() {
        return this.checkViewPortMode('tablet');
    }

    private checkViewPortMode(mode: ViewportBreakpoint) {
        return this.viewportBreakpoint === mode;
    }

    public userFlowType(): Promise<userRegistrationFlowType> {
        return this.flowTypeService.getFlowType();
    }
}
