import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {Tax, TaxesService} from '../../../../services/taxes.service';
import {cloneDeep} from 'lodash';
import {defer, deleteFromArray, isFinite, isSameObjectsLayout, updateObject} from '../../../../lib/utils';
import {PopupService} from '../../../../services/popup.service';


type ListState = 'loading' | 'error' | 'empty' | 'list';

interface State {
    sort : {
        by : string;
        direction : number;
    };
}


@Component({
    selector: 'taxes',
    templateUrl: './taxes.component.html',
    styleUrls: [ './taxes.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'taxes-editor',
    }
})
export class TaxesSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public listState : ListState;

    public state : State;

    public stateChangeDebounceTimer : any = null;

    public isSaving : boolean = false;

    public isDeleting : boolean = false;

    public taxes : Tax[];

    @ViewChild('editor')
    public editor : PopupComponent;

    public taxToEdit : Tax;

    public isEditorFormValid : boolean = false;

    public readonly sortOptions : any = [
        {
            value: 'name',
            display: 'settings.taxes.name'
        },
        {
            value: 'value',
            display: 'settings.taxes.tax'
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
        private taxesService : TaxesService,
    ) {
        this.listState = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.taxes.page_title');
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
            this.taxesService.fetchTaxes(),
            this.taxesService.fetchTaxesListState()
        ).subscribe(
            ([ taxes, state ] : [ Tax[], any ]) => {
                state = state || {};

                if (isSameObjectsLayout(this.defaultState, state)) {
                    this.state = state;
                } else {
                    this.state = updateObject(this.defaultState, state);
                    this.saveState();
                }

                this.taxes = this.sortTaxes(taxes);
                this.listState = this.taxes.length ? 'list' : 'empty';
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

    public sortTaxes (taxes : Tax[]) : Tax[] {
        if (!taxes || !taxes.length) {
            return taxes;
        }

        const { by, direction } = this.state.sort;

        return taxes.sort((t1, t2 ) => {
            let a : any = t1[by],
                b : any = t2[by];

            if (by === 'value') {
                return ((Number(a) - Number(b)) || (t1.id - t2.id)) * direction;
            }

            a = a === null ? '' : String(a);
            b = b === null ? '' : String(b);

            return (a.localeCompare(b) || (t1.id - t2.id)) * direction;
        });
    }

    public saveState () : void {
        if (this.stateChangeDebounceTimer !== null) {
            clearTimeout(this.stateChangeDebounceTimer);
        }

        this.stateChangeDebounceTimer = setTimeout(() => {
            this.stateChangeDebounceTimer = null;
            this.taxesService.saveTaxesListState(this.state);
        }, 200);
    }

    public onOrderChange () : void {
        this.taxes = this.sortTaxes(this.taxes);
        this.saveState();
    }

    public onDelete (tax : Tax) : void {
        if (this.isDeleting) {
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.taxes.confirm_delete', { tax: tax.name } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.isDeleting = true;

                this.taxesService.deleteTax(tax.id).subscribe(
                    () => {
                        deleteFromArray(this.taxes, tax);
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

    public onCreate () : void {
        this.taxToEdit = new Tax();
        this.isEditorFormValid = false;
        this.validate();
        defer(() => this.editor.activate());
    }

    public validate () : void {
        defer(() => {
            const name = (this.taxToEdit.name || '').trim();
            const value = this.taxToEdit.value;
            this.isEditorFormValid = name.length > 0 && isFinite(value) && value >= 0 && value <= 1000000;
        });
    }

    public onSave () : void {
        if (!this.isEditorFormValid || this.isSaving || this.isDeleting) {
            return;
        }

        this.isSaving = true;

        this.taxesService.createTax(this.taxToEdit).subscribe(
            tax => {
                this.taxes.push(tax);
                this.taxes = this.sortTaxes(this.taxes);
                this.onHideEditor();
                this.isSaving = false;
            },
            () => {
                // TODO: show error toast
                this.isSaving = false;
            }
        );
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.editor.deactivate().then(() => {
            this.taxToEdit = null;
        });
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

