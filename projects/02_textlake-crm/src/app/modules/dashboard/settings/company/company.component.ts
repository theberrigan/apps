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

type State = 'loading' | 'error' | 'editor';

@Component({
    selector: 'company',
    templateUrl: './company.component.html',
    styleUrls: [ './company.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'company-editor',
    }
})
export class CompanySettingsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isSaving : boolean = false;

    public state : State;

    public form : FormGroup;

    public timezoneOptions : any[];

    public langOptions : any[];

    // TODO: check company:edit feature
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
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.company.page_title');

        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.timezoneOptions = this.datetimeService.fetchTimezones();

        this.addSub(zip(
            this.langService.fetchLanguages({
                preferredOnly: true,
                addDefault: true
            }),
            this.companyService.getCompany()
        ).subscribe(
            ([ langs, company ] : [ any[], Company ]) => {
                this.langOptions = langs;

                this.form = this.formBuilder.group({
                    preferredLanguage: [ company.preferredLanguage ],
                    name: [ company.name ],
                    email: [ company.email ],
                    phone: [ company.phone ],
                    fax: [ company.fax ],
                    street: [ company.street ],
                    street2: [ company.street2 ],
                    city: [ company.city ],
                    zipCode: [ company.zipCode ],
                    state: [ company.state ],
                    country: [ company.country ],
                    timeZone: [ company.timeZone ],
                    tin: [ company.tin ],
                    bankName: [ company.bankName ],
                    bankAccount: [ company.bankAccount ],
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

    public onSave () : void {
        if (this.isSaving || !this.form) {
            return;
        }

        this.isSaving = true;

        this.addSub(this.companyService.updateCompany(this.form.getRawValue()).subscribe(
            () => {
                this.form.markAsPristine();
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.company.save_success__label' ]
                });
            },
            () => {
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.company.save_error__label' ]
                });
            }
        ));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

