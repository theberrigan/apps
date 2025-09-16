import {AfterViewInit, Component, EventEmitter, NgZone, OnDestroy, OnInit, Output, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {RouterService} from '../../../../services/router.service';
import {PopupService} from '../../../../services/popup.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {UserData, UserService} from '../../../../services/user.service';
import {from, Subscription, zip} from 'rxjs';
import {OffersService, OffersSettings} from '../../../../services/offers.service';
import {ProjectsService, ProjectsSettings} from '../../../../services/projects.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {LANGS} from '../../../../services/lang.service';
import {first} from 'rxjs/operators';
import {ToastService} from '../../../../services/toast.service';
import {TranslatorsService, TranslatorsSettings} from '../../../../services/translators.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';

type State = 'loading' | 'ready' | 'error';

@Component({
    selector: 'profile',
    templateUrl: './profile.component.html',
    styleUrls: [ './profile.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'profile',
    }
})
export class ProfileComponent implements AfterViewInit, OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isActive : boolean = false;

    public isSaving : boolean = false;

    public state : State;

    @ViewChild('popup')
    public popup : PopupComponent;

    public userData : UserData;

    public reqSub : Subscription;

    public offersSettings : OffersSettings;

    public projectsSettings : ProjectsSettings;

    public translatorsSettings : TranslatorsSettings;

    public offersStatuses : any;

    public projectsStatuses : any;

    public form : FormGroup;

    public languageOptions : any[];

    public sampleDate : Date;

    @Output()
    public onShowEmailVerificationPopup : EventEmitter<void> = new EventEmitter<void>();

    public readonly dateFormatOptions = [
        {
            label: 'settings.profile.date_group_popular',
            formats: [
                'D MMM YY',
                'MMM D, YY',
                'DD/MM/YYYY',
                'DD.MM.YYYY',
                'MM/DD/YYYY',
            ]
        },
        {
            label: 'settings.profile.date_group_other',
            formats: [
                'DD/MM/YY',
                'DD.MM.YY',
                'MM.DD.YYYY',
                'MM/DD/YY',
                'MM.DD.YY',
                'YYYY/MM/DD',
                'YYYY.MM.DD',
                'YY/MM/DD',
                'YY.MM.DD',
                'YYYY/DD/MM',
                'YYYY.DD.MM',
                'YY/DD/MM',
                'YY.DD.MM',
            ]
        },
    ];

    public readonly timeFormatOptions = [
        {
            format: 'HH:mm',
            suffix: 'settings.profile.time_suffix_24'
        },
        {
            format: 'hh:mm A',
            suffix: 'settings.profile.time_suffix_12'
        }
    ];

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private routerService : RouterService,
        private formBuilder : FormBuilder,
        private popupService : PopupService,
        private deviceService : DeviceService,
        private userService : UserService,
        private offersService : OffersService,
        private projectsService : ProjectsService,
        private zone : NgZone,
        private toastService : ToastService,
        private translatorsService : TranslatorsService,
    ) {
    }

    public ngAfterViewInit () : void {
        this.zone.onStable.pipe(first()).subscribe(() => {
            this.route.queryParams.subscribe((queryParams) => {
                this.isActive = queryParams.z === 'profile';

                if (this.isActive) {
                    this.showPopup();
                } else {
                    this.hidePopup();
                }
            });
        });
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public showPopup () : void {
        if (this.state === 'loading') {
            return;
        }

        this.state = 'loading';
        this.popup.showSpinner();
        this.popup.activate();

        this.userData = this.userService.getUserData();

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.languageOptions = LANGS.map(lang => ({
            display: lang.nameKey,
            value: lang.code
        }));

        this.sampleDate = new Date(2077, 11, 31, 23, 59, 59);

        this.reqSub = zip(
            this.offersService.fetchOfferStatuses(),
            this.offersService.fetchOffersSettings(),
            this.projectsService.fetchProjectsStatuses(),
            this.projectsService.fetchProjectsSettings(),
            this.translatorsService.fetchTranslatorsSettings(),
        ).subscribe(([
            offersStatuses,
            offersSettings,
            projectsStatuses,
            projectsSettings,
            translatorsSettings
        ]) => {
            this.offersStatuses = offersStatuses;
            this.offersSettings = offersSettings;
            this.projectsStatuses = projectsStatuses;
            this.projectsSettings = projectsSettings;
            this.translatorsSettings = translatorsSettings;

            this.form = this.formBuilder.group({
                email: [ this.userData.profile.user.email ],
                language: [ this.userData.profile.language ],
                datetimeDisplayFormat: this.formBuilder.group({
                    date: [ this.userData.settings.formats.date.display ],
                    time: [ this.userData.settings.formats.time.display ]
                }),
                datetimeSelectFormat: this.formBuilder.group({
                    date: [ this.userData.settings.formats.date.select ],
                    time: [ this.userData.settings.formats.time.select ]
                }),
                offersColorizeEntireRow: this.offersSettings.colorizeEntireRow,
                projectsColorizeEntireRow: this.projectsSettings.colorizeEntireRow,
                translatorsColorizeEntireRow: this.translatorsSettings.colorizeEntireRow,
                offersStatusesColors: this.formBuilder.group(
                    offersStatuses.reduce((acc, status) => {
                        acc[status.key] = [ offersSettings.statusesColors[status.key] ];
                        return acc;
                    }, {})
                ),
                projectsStatusesColors: this.formBuilder.group(
                    projectsStatuses.reduce((acc, status) => {
                        acc[status.key] = [ projectsSettings.statusesColors[status.key] ];
                        return acc;
                    }, {})
                )
            });

            console.log(offersStatuses,
                offersSettings,
                projectsStatuses,
                projectsSettings);

            this.popup.showBox();
            this.state = 'ready';
        }, () => {
            this.popup.showBox();
            this.state = 'error';
        });

        this.addSub(this.reqSub);
    }

    public hidePopup () : void {
        if (this.reqSub) {
            this.reqSub.unsubscribe();
        }

        this.popup.deactivate().then(() => {
            this.form = null;
        });
    }

    public onSave () : void {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;
        this.form.disable();

        const formValue = this.form.getRawValue();

        this.userData.profile.user.email = formValue.email;
        this.userData.profile.language = formValue.language;
        this.userData.settings.formats.date.display = formValue.datetimeDisplayFormat.date;
        this.userData.settings.formats.time.display = formValue.datetimeDisplayFormat.time;
        this.userData.settings.formats.datetime.display = [
            formValue.datetimeDisplayFormat.date,
            formValue.datetimeDisplayFormat.time
        ].join(' ');
        this.userData.settings.formats.date.select = formValue.datetimeSelectFormat.date;
        this.userData.settings.formats.time.select = formValue.datetimeSelectFormat.time;
        this.userData.settings.formats.datetime.select = [
            formValue.datetimeSelectFormat.date,
            formValue.datetimeSelectFormat.time
        ].join(' ');

        this.offersSettings.statusesColors = formValue.offersStatusesColors;
        this.projectsSettings.statusesColors = formValue.projectsStatusesColors;

        this.offersSettings.colorizeEntireRow = formValue.offersColorizeEntireRow;
        this.projectsSettings.colorizeEntireRow = formValue.projectsColorizeEntireRow;
        this.translatorsSettings.colorizeEntireRow = formValue.translatorsColorizeEntireRow;

        Promise.all([
            this.userService.updateUserData({ data: this.userData }),
            this.offersService.saveOffersSettings(this.offersSettings),
            this.projectsService.saveProjectsSettings(this.projectsSettings),
            this.translatorsService.saveTranslatorsSettings(this.translatorsSettings)
        ]).then(() => {
            this.userData = this.userService.getUserData();
            this.form.markAsPristine();
            this.form.enable();
            this.isSaving = false;
            this.toastService.create({
                message: [ `settings.profile.save_success` ]
            });
        }).catch(() => {
            this.form.enable();
            this.isSaving = false;
            this.toastService.create({
                message: [ `settings.profile.save_failed` ]
            });
        });
    }

    public updateVerificationState () : void {
        this.userData.profile.primaryEmailVerified = this.userService.getUserData().profile.primaryEmailVerified;
    }

    public onVerifyEmail () : void {
        this.onShowEmailVerificationPopup.emit();
    }

    public onCloseRequest (byOverlay? : boolean) : void {
        if (this.isSaving || byOverlay) {
            return;
        }

        if (!this.form || this.form.pristine) {
            this.routerService.unsetQueryZ();
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.profile.confirm_discard__message' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.routerService.unsetQueryZ();
            }
        });
    }
}
