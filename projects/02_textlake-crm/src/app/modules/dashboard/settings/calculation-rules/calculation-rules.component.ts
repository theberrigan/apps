import {Component, OnDestroy, ViewEncapsulation} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UiService} from '../../../../services/ui.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {DatetimeService} from '../../../../services/datetime.service';
import {LangService} from '../../../../services/lang.service';
import {Company, CompanyService} from '../../../../services/company.service';
import {PopupService} from '../../../../services/popup.service';
import {ToastService} from '../../../../services/toast.service';
import {CalcService, RoundingRule} from '../../../../services/calc.service';

type State = 'loading' | 'error' | 'editor';

@Component({
    selector: 'calculation-rules',
    templateUrl: './calculation-rules.component.html',
    styleUrls: [ './calculation-rules.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'calculation-rules',
    }
})
export class CalculationRulesComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isSaving : boolean = false;

    public state : State;

    public form : FormGroup;

    public readonly ruleOptions = [
        {
            display: 'settings.calc_rules.rules.up',
            value: 'ROUND_UP'
        },
        {
            display: 'settings.calc_rules.rules.down',
            value: 'ROUND_DOWN'
        },
        {
            display: 'settings.calc_rules.rules.ceiling',
            value: 'ROUND_CEILING'
        },
        {
            display: 'settings.calc_rules.rules.floor',
            value: 'ROUND_FLOOR'
        },
        {
            display: 'settings.calc_rules.rules.half_up',
            value: 'ROUND_HALF_UP'
        },
        {
            display: 'settings.calc_rules.rules.half_down',
            value: 'ROUND_HALF_DOWN'
        },
        {
            display: 'settings.calc_rules.rules.half_even',
            value: 'ROUND_HALF_EVEN'
        },
    ];

    public exampleValues : any[][];

    constructor (
        private router : Router,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private popupService : PopupService,
        private datetimeService : DatetimeService,
        private langService : LangService,
        private companyService : CompanyService,
        private toastService : ToastService,
        private calcService : CalcService,
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.calc_rules.page_title');

        this.generateExample();

        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(
            this.companyService.fetchCalcRule().subscribe((calcRule) => {
                this.form = this.formBuilder.group({
                    calcRule: [ calcRule ],
                });

                this.state = 'editor';
            },
            () => this.state = 'error'
        ));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            if (this.state !== 'editor' || this.form.pristine) {
                resolve(true);
                return;
            }

            this.popupService.confirm({
                message: [ 'guards.discard' ],
            }).subscribe(({ isOk }) => resolve(isOk));
        });
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public generateExample () : void {
        const exampleValues = [];
        const values = [ 5.5, 2.5, 1.6, 1.1, 1.0, -1.0, -1.1, -1.6, -2.5, -5.5 ];

        exampleValues.push([
            {
                isBold: true,
                i18n: true,
                isNumber: false,
                rule: null,
                value: 'settings.calc_rules.number'
            },
            ...values.map(value => ({
                isBold: true,
                i18n: false,
                isNumber: true,
                rule: null,
                value
            }))
        ]);

        this.ruleOptions.forEach(rule => {
            exampleValues.push([
                {
                    isBold: true,
                    i18n: true,
                    isNumber: false,
                    rule: rule.value,
                    value: rule.display
                },
                ...values.map(value => ({
                    isBold: false,
                    i18n: false,
                    isNumber: true,
                    rule: null,
                    value: this.calcService.round(value, <RoundingRule>rule.value)
                }))
            ]);
        });

        this.exampleValues = exampleValues;
    }

    public get currentRule () : RoundingRule {
        return this.form ? this.form.controls['calcRule'].value : undefined;
    }

    public onSave () : void {
        if (this.isSaving || !this.form) {
            return;
        }

        this.isSaving = true;

        const { calcRule } = this.form.getRawValue();

        this.addSub(this.companyService.saveCalcRule(calcRule).subscribe(
            calcRule => {
                this.form.setValue({ calcRule });
                this.form.markAsPristine();
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.calc_rules.save_ok' ]
                });
            },
            () => {
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.calc_rules.save_error' ]
                });
            }
        ));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

