import {Component, ViewChild, ViewEncapsulation} from '@angular/core';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {cloneDeep, merge} from 'lodash';
import {Translator, TranslatorsService, TranslatorsSettings} from '../../../services/translators.service';
import {CompanyService} from '../../../services/company.service';
import {LangService} from '../../../services/lang.service';
import {ColorService} from '../../../services/color.service';
import {DomSanitizer, SafeStyle} from '@angular/platform-browser';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';

type ListState = 'init' | 'loading' | 'error' | 'empty' | 'list';

@Component({
    selector: 'translators',
    templateUrl: './translators.component.html',
    styleUrls: [ './translators.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'translators',
    }
})
export class TranslatorsComponent {
    public readonly sizeOptions : number[] = [ 10, 25, 50, 75, 100 ];

    public readonly sortOptions : any[] = [
        {
            display: 'settings.translators.list.last_name__label',
            value: 'lastName'
        },
        {
            display: 'settings.translators.list.first_name__label',
            value: 'firstName'
        },
        {
            display: 'settings.translators.list.middle_name__label',
            value: 'middleName'
        },
        {
            display: 'settings.translators.list.native_language__label',
            value: 'nativeLanguage'
        },
        {
            display: 'settings.translators.list.email__label',
            value: 'email'
        },
        {
            display: 'settings.translators.list.phone__label',
            value: 'phone'
        }
    ];

    public langs : { [ langKey : string ] : string } = {};

    public langOptions : any[] = [
        {
            value: null,
            display: ''
        }
    ];

    public translationTypeOptions : any[] = [
        {
            value: null,
            display: ''
        }
    ];

    public readonly defaultState : any = {
        view: {
            tablet: 'grid-detailed',
            desktop: 'grid-detailed',
        },
        sort: {
            by: this.sortOptions[0].value,
            direction: 1
        },
        sidebar: {
            isActive: true,
            filters: {
                name: '',
                city: '',
                email: '',
                phone: '',
                languageFrom: this.langOptions[0].value,
                languageTo: this.langOptions[0].value,
                translationTypeId: this.translationTypeOptions[0].value,
                comment: ''
            },
            collapse: {
                options: false,
                filters: false
            }
        }
    };

    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : any;

    public orderDebounceTimer : any = null;

    public stateChangeDebounceTimer : any = null;

    public listState : ListState;

    public filtersForm : FormGroup;

    public canEdit : boolean;

    public translatorsRequest : Subscription = null;

    public translators : Translator[];

    public translatorsSettings : TranslatorsSettings;

    public colors : {
        [ key : number ] : SafeStyle
    } = {};

    @ViewChild('sidebar')
    public sidebar : SidebarComponent;

    public constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private sanitizer: DomSanitizer,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private translatorsService : TranslatorsService,
        private companyService : CompanyService,
        private langService : LangService,
        private colorService : ColorService,
    ) {
        this.state = this.defaultState;
        this.listState = 'init';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.translators.list.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.filtersForm = this.formBuilder.group({
            name: [ '' ],
            city: [ '' ],
            email: [ '' ],
            phone: [ '' ],
            languageFrom: [ null ],
            languageTo: [ null ],
            translationTypeId: [ null ],
            comment: [ '' ]
        });

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.translatorsService.fetchTranslatorsListState(),
            this.companyService.fetchTranslationTypes(),
            this.langService.fetchLanguages(),
            this.translatorsService.fetchTranslatorsSettings(),
        ).subscribe(([ state, translationTypes, langs, translatorsSettings ]) => {
            this.langOptions = [ ...this.langOptions, ...langs ];
            this.translatorsSettings = translatorsSettings;
            //this.translatorsSettings.colorizeEntireRow = true;

            langs.forEach(lang => {
                this.langs[lang.value] = lang.display;
            });

            translationTypes.forEach(tt => {
                this.translationTypeOptions.push({
                    display: tt.name,
                    value: tt.id
                });
            });

            state = state || {};

            if (isSameObjectsLayout(this.defaultState, state)) {
                this.state = state;
            } else {
                this.state = updateObject(this.defaultState, state);
                this.saveState();
            }

            this.filtersForm.setValue(this.state.sidebar.filters);

            this.fetchTranslators('init');
        }));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.canEdit = userData.features.can('edit:translators');
    }

    public onOrderChange () : void {
        if (this.orderDebounceTimer !== null) {
            clearTimeout(this.orderDebounceTimer);
        }

        this.orderDebounceTimer = setTimeout(() => {
            this.orderDebounceTimer = null;
            this.translators = this.sortTranslators(this.translators);
        }, 200);
    }

    public onSidebarToggle (isActive : boolean) : void {
        this.updateState({
            sidebar: { isActive }
        });
    }

    public onSidebarSectionCollapse (section : string, isCollapsed : boolean) : void {
        this.updateState({
            sidebar: {
                collapse: {
                    [ section ]: isCollapsed
                }
            }
        });
    }

    public onFiltersSubmit (withReset : boolean = false) : void {
        if (this.viewportBreakpoint !== 'desktop' && this.sidebar) {
            this.sidebar.deactivate();
        }

        if (withReset) {
            this.filtersForm.reset(this.defaultState.sidebar.filters);
        }

        this.updateState({
            sidebar: {
                filters: this.filtersForm.getRawValue()
            }
        });

        this.fetchTranslators('loading');
    }

    public updateState (updateWith : any = null) : void {
        if (this.state) {
            this.state = merge({}, this.state, updateWith);
            this.saveState();
        }
    }

    public saveState () : void {
        if (this.stateChangeDebounceTimer !== null) {
            clearTimeout(this.stateChangeDebounceTimer);
        }

        this.stateChangeDebounceTimer = setTimeout(() => {
            this.stateChangeDebounceTimer = null;
            this.translatorsService.saveTranslatorsListState(this.state);
        }, 200);
    }

    public get isDesktopSidebarActive () : boolean {
        return this.listState !== 'init' && this.state && this.state.sidebar.isActive;
    }

    public fetchTranslators (listState : ListState) : void {
        this.listState = listState;

        if (this.translatorsRequest) {
            this.translatorsRequest.unsubscribe();
            this.translatorsRequest = null;
        }

        const filters : any = cloneDeep(this.state.sidebar.filters);

        Object.keys(filters).forEach(key => {
            const value = filters[key];
            const valueStr = String(value).trim();

            if (valueStr === '' || value === '' || value === null || value === undefined) {
                delete filters[key];
            } else {
                filters[key] = valueStr;
            }
        });

        const sub = this.translatorsRequest = this.translatorsService.fetchTranslators(filters).subscribe(
            (translators : Translator[]) => {
                console.log(translators);
                this.translators = this.sortTranslators(translators || []);
                if (this.translatorsSettings.colorizeEntireRow) {
                    this.translators.forEach(translator => {
                        this.colors[translator.id] = this.sanitizer.bypassSecurityTrustStyle(translator.color ? (
                            'background-color: #' + translator.color + ' !important; ' +
                            'color: ' + this.colorService.getContrastingColor(translator.color) + ' !important'
                        ) : '');
                    });
                }
                this.colors = { ...this.colors };
                this.listState = this.translators.length ? 'list' : 'empty';

                if (sub === this.translatorsRequest) {
                    this.translatorsRequest.unsubscribe();
                    this.translatorsRequest = null;
                }
            },
            () => {
                this.listState = 'error';
                this.translators = [];

                if (sub === this.translatorsRequest) {
                    this.translatorsRequest.unsubscribe();
                    this.translatorsRequest = null;
                }
            }
        );
    }

    public sortTranslators (translators : Translator[]) : Translator[] {
        if (!translators.length) {
            return translators;
        }

        const orderBy = this.state.sort.by;
        const orderDir = this.state.sort.direction;

        translators = [ ...translators ].sort((t1, t2) => {
            let a : any = t1[orderBy] === null ? '' : String(t1[orderBy]),
                b : any = t2[orderBy] === null ? '' : String(t2[orderBy]);

            if (orderBy === 'nativeLanguage') {
                a && (a = this.getLanguageName(a));
                b && (b = this.getLanguageName(b));
            }

            return (a.localeCompare(b) || (t1.id - t2.id)) * orderDir;
        });

        return translators;
    }

    public getLanguageName (code : string) : string {
        return this.langs[code] || code;
    }

    public get viewType () : 'grid' | 'grid-detailed' | 'table' {
        const bp = this.viewportBreakpoint;

        if (bp === 'desktop') {
            return this.state.view.desktop;
        } else {
            return bp === 'tablet' ? 'grid-detailed' : 'grid';
        }
    }

    public goToTranslator (translator : Translator) : void {
        this.router.navigateByUrl('/dashboard/translator/' + translator.id);
    }

}
