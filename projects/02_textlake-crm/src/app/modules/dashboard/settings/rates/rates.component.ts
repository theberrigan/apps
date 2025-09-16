import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {Rate, RatesService} from '../../../../services/rates.service';
import {PopupService} from '../../../../services/popup.service';
import {
    defer,
    deleteFromArray,
    isSameObjectsLayout,
    updateObject
} from '../../../../lib/utils';
import {cloneDeep, forIn} from 'lodash';


type ListState = 'loading' | 'error' | 'empty' | 'list';
type EditorMode = 'create' | 'edit';

interface State {
    sort : {
        by : string;
        direction : number;
    };
}


@Component({
    selector: 'rates',
    templateUrl: './rates.component.html',
    styleUrls: [ './rates.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'rates-editor',
    }
})
export class RatesSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public listState : ListState;

    public state : State;

    public stateChangeDebounceTimer : any = null;

    public isSaving : boolean = false;

    public isDeleting : boolean = false;

    public rates : Rate[];

    public editorMode : EditorMode;

    @ViewChild('editor')
    public editor : PopupComponent;

    public isEditorFormValid : boolean = false;

    public rateToEdit : Rate;

    public rateToEditIndex : number;

    public readonly sortOptions : any = [
        {
            value: 'name',
            display: 'settings.rates.list.name'
        },
        {
            value: 'global',
            display: 'settings.rates.list.global'
        },
        {
            value: 'enabled',
            display: 'settings.rates.list.enabled'
        },
        {
            value: 'description',
            display: 'settings.rates.list.description'
        },
    ];

    public readonly defaultState : State = {
        sort: {
            by: this.sortOptions[0].value,
            direction: 1
        }
    };

    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private popupService : PopupService,
        private ratesService : RatesService,
    ) {
        this.listState = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.rates.list.page_title');
        this.state = cloneDeep(this.defaultState);

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.ratesService.fetchRates(),
            this.ratesService.fetchRatesListState()
        ).subscribe(
            ([ rates, state ] : [ Rate[], any ]) => {
                state = state || {};

                if (isSameObjectsLayout(this.defaultState, state)) {
                    this.state = state;
                } else {
                    this.state = updateObject(this.defaultState, state);
                    this.saveState();
                }

                this.rates = this.sortRates(rates);
                this.listState = this.rates.length ? 'list' : 'empty';
            },
            () => {
                this.listState = 'error';
            }
        ));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {

    }


    public sortRates (rates : Rate[]) : Rate[] {
        if (!rates || !rates.length) {
            return rates;
        }

        const { by, direction } = this.state.sort;

        return rates.sort((r1, r2) => {
            let a : any = r1[by],
                b : any = r2[by];

            if (typeof(a) === 'boolean' || typeof(b) === 'boolean') {
                return ((Number(a) - Number(b)) || (r1.id - r2.id)) * direction;
            }

            a = a === null ? '' : String(a);
            b = b === null ? '' : String(b);

            return (a.localeCompare(b) || (r1.id - r2.id)) * direction;
        });
    }

    public saveState () : void {
        if (this.stateChangeDebounceTimer !== null) {
            clearTimeout(this.stateChangeDebounceTimer);
        }

        this.stateChangeDebounceTimer = setTimeout(() => {
            this.stateChangeDebounceTimer = null;
            this.ratesService.saveRatesListState(this.state);
        }, 200);
    }

    public onOrderChange () : void {
        this.rates = this.sortRates(this.rates);
        this.saveState();
    }

    public onDelete (rate : Rate) : void {
        this.popupService.confirm({
            message: [ 'settings.rates.list.confirm_delete', { rate: rate.name } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.isDeleting = true;

                this.ratesService.deleteRate(rate.id).subscribe(
                    () => {
                        deleteFromArray(this.rates, rate);
                        this.isDeleting = false;
                    },
                    () => {
                        // TODO: show error toast
                        this.isDeleting = false;
                    }
                );
            }
        });
    }

    public onEdit (rate : Rate) : void {
        this.editorMode = 'edit';
        this.rateToEdit = cloneDeep(rate);
        this.rateToEditIndex = this.rates.indexOf(rate);
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public onCreate () : void {
        this.editorMode = 'create';
        this.rateToEdit = new Rate();
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public prepareEditor () : void {
        this.isEditorFormValid = false;
        this.validate();
    }

    public validate () : void {
        defer(() => {
            this.isEditorFormValid = (this.rateToEdit.name || '').trim().length > 0;
        });
    }

    public onSave () : void {
        if (!this.isEditorFormValid || this.isSaving || this.isDeleting) {
            return;
        }

        this.isSaving = true;

        if (this.editorMode === 'create') {
            this.ratesService.createRates(this.rateToEdit).subscribe(
                rate => {
                    this.rates.push(rate);
                    this.rates = this.sortRates(this.rates);
                    this.onHideEditor();
                    this.isSaving = false;
                },
                () => {
                    // TODO: show error toast
                    this.isSaving = false;
                },
            );
        } else {
            this.ratesService.updateRates(this.rateToEdit).subscribe(
                rate => {
                    this.rates[this.rateToEditIndex] = rate;
                    this.rates = this.sortRates(this.rates);
                    this.onHideEditor();
                    this.isSaving = false;
                },
                () => {
                    // TODO: show error toast
                    this.isSaving = false;
                }
            );
        }
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.editor.deactivate().then(() => {
            this.editorMode = null;
            this.rateToEdit = null;
            this.rateToEditIndex = null;
        });
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

