import {
    AfterContentInit,
    ChangeDetectionStrategy, ChangeDetectorRef,
    Component, ContentChildren,
    DoCheck, ElementRef,
    forwardRef, HostBinding, HostListener, Input, NgZone,
    OnChanges, OnDestroy,
    OnInit, QueryList, SimpleChanges, TemplateRef, ViewChild, ViewContainerRef,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {
    DropdownItemComponent,
    DropdownOptionSelectionStateChangeEvent
} from './dropdown-item.component';
import {DropdownGroupComponent} from './dropdown-group.component';
import {DomService} from '../../services/dom.service';
import {DeviceService} from '../../services/device.service';
import { merge, Subject } from 'rxjs';
import {
    debounceTime,
    distinctUntilChanged,
    map,
    startWith,
    takeUntil
} from 'rxjs/operators';
import {DebugService} from '../../services/debug.service';

/*
* a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ
* https://material.angular.io/components/select/examples
* TODO Checklist:
* - Не всегда срабатывает поиск
* - Не всегда во время поиска список выравнивается на всю ширину меню
* - required && (in)valid state
* - Мобильный (оверлейный) вариант дропдауна
* - Сделать пункты шире для тача и приделать галочки
* 6. Поведение при сбросе значения
* 8. Логика при удалении, добавлении, модификации (не забыть перерисовку)
* 11. В CSS разобраться с временными и недостающими свойствами типа pointer-events, will-change
* 12. Протестировать в браузерах
* 16. При активации списка нужно устанавливать z-index
* 17. Поддержка template-driven и reactive форм
* 18. Как соотносится с валидаторами
* 25. ErrorStateMatcher,
* 29. role, aria-*, scope
* */

/*
openDropdown () {
    if (mobile) {
        openListInPopup();
    }
    searchFocus();
    scrollToActiveOrToTop();
    _updateDisplayState();
}

close () {

    _updateDisplayState();
}

selectByClick () {
    checkSoloItemAndGroupsAndDeselectUnwantedItems();
    writeToModel();
    _updateDisplayState();
    notifyOuterSubscribers();
}

reset () {
    findDefaultItem()
        - useFirstAsDefault ?
}

disable () {
    closeDropdown()
    resetOnDisable
}

*/

type AnchorPoint = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

const DROPDOWN_MAX_WIDTH = 480;
const DROPDOWN_MAX_HEIGHT = 480;

@Component({
    selector: 'dropdown',
    exportAs: 'dropdown',
    templateUrl: './dropdown.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.Default,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => DropdownComponent),
            multi: true
        }
    ],
    host: {
        'class': 'dropdown',
        '[class.dropdown_multiple]': '_multiple',
        '[class.dropdown_touch]': '_isTouch',
        '[class.dropdown_disabled]': '_disabled',
        '[class.dropdown_active]': 'isActive',
        '[class.dropdown_dropdown-wider]': 'isWider',
        '[class.dropdown_empty]': 'empty',
        '[class.dropdown_anchor_top-left]': `anchorPoint === 'top-left'`,
        '[class.dropdown_anchor_top-right]': `anchorPoint === 'top-right'`,
        '[class.dropdown_anchor_bottom-left]': `anchorPoint === 'bottom-left'`,
        '[class.dropdown_anchor_bottom-right]': `anchorPoint === 'bottom-right'`,
    }
})
export class DropdownComponent implements OnInit, OnDestroy, DoCheck, OnChanges, AfterContentInit, ControlValueAccessor {
    // Options
    // -----------------------

    public _placeholder : string = '';

    @Input()
    public get placeholder () : string {
        return this._placeholder;
    }

    public set placeholder (value : string) {
        this._placeholder = String(value || '').trim();
    }

    public _disabled : boolean = false;

    @Input()
    public get disabled () : boolean {
        return this._disabled;
    }

    public set disabled (value : boolean) {
        if ((this._disabled = this.domService.parseBooleanAttr(value))) {
            this.deactivate();
        }
    }

    public _search : boolean = false;

    @Input()
    public get search () : boolean {
        return this._search;
    }

    public set search (value : boolean) {
        // console.log('Set search');
        if (!(this._search = this.domService.parseBooleanAttr(value))) {
            this.searchString = '';
            this._applySearchRegexp(null);
            this._updateDisplayState();
        }
    };

    public _useFirstAsDefault : boolean = false;

    @Input()
    public get useFirstAsDefault () : boolean {
        return this._useFirstAsDefault;
    }

    public set useFirstAsDefault (value : boolean) {
        this._useFirstAsDefault = this.domService.parseBooleanAttr(value);
    };

    public _multiple : boolean = false;

    @Input()
    public get multiple () : boolean {
        return this._multiple;
    }

    public set multiple (value : boolean) {
        this._multiple = this.domService.parseBooleanAttr(value);
    };

    @Input()
    public searchCallback : (text : string) => void;

    // Views
    // --------------

    @ViewChild('elDisplay')
    public elDisplay : any;

    @ViewChild('elDropdown')
    public elDropdown : any;

    @ViewChild('elScroll')
    public elScroll : any;

    @ViewChild('elList')
    public elList : any;

    @ViewChild('elSearchInput')
    public elSearchInput : any;

    @ViewChild('displayContainer', { read: ViewContainerRef })
    public elDisplayContainer : ViewContainerRef;

    @ContentChildren(DropdownItemComponent, { descendants: true })
    public _items : QueryList<DropdownItemComponent>;

    @ContentChildren(DropdownGroupComponent)
    public _itemGroups : QueryList<DropdownGroupComponent>;

    public _isTouch : boolean = true;

    // @ViewChild('listTemplate', { read: TemplateRef })
    // public _listTemplate : TemplateRef<any>;
    //
    // @ViewChild('listTouchTemplate', { read: TemplateRef })
    // public _listTouchTemplate : TemplateRef<any>;
    //
    // @ViewChild('listDesktopContainer', { read: ViewContainerRef })
    // public _listDesktopContainer : ViewContainerRef;

    //
    // -----------

    public dropdownWidth : number = null;

    public dropdownHeight : number = null;

    public _dropdownBordersWidth : any = null;

    public isListFullWidth : boolean = false;

    public isWider : boolean = false;

    public anchorPoint : AnchorPoint = null;

    public isActive : boolean = false;

    public displayText : string = '';

    public displayStyle : 'default' | 'placeholder' | 'hidden' = 'hidden';

    public displayType : 'template' | 'html' = 'html';

    public displayTemplate : TemplateRef<any>;

    public displayContext : any = null;

    public searchString : string = '';

    public searchSubject : Subject<any> = new Subject<any>();

    public _onDestroy : Subject<any> = new Subject<any>();

    public _selection : any;

    public _searchRegexp : RegExp;

    public empty : boolean = false;

    public _model : any;

    public onChange : any = (_: any) => {};

    public onTouched : any = () => {};

    constructor (
        private _ngZone : NgZone,
        private cdr : ChangeDetectorRef,
        private elRef : ElementRef,
        private domService : DomService,
        private deviceService : DeviceService,
        private debug : DebugService
    ) {}

    // Angular hooks
    // --------------------------------------

    public ngOnInit () : void {
        this._isTouch = this.deviceService.device.touch;

        // if(!this._isTouch) {
        //     this._listDesktopContainer.createEmbeddedView(this._listTemplate);
        // }
        // this._listTemplateCurrent = this._isTouch ? this._listTemplateTouch : this._listTemplateDesktop;
    }

    public ngOnDestroy () : void {
        this._onDestroy.next();
    }

    public ngDoCheck () : void {

    }

    public ngOnChanges (changes : SimpleChanges) : void {
        // ('ngOnChanges');
    }

    public ngAfterContentInit () : void {
        // console.log('--- INIT START ---');

        this.searchSubject.pipe(
            map(text => text.trim()),
            debounceTime(300),
            distinctUntilChanged()
        ).subscribe(searchString => {
            if (!this.isActive) {
                return;
            }

            if (this.searchCallback) {
                this.searchCallback(searchString);
            } else {
                this._applySearchRegexp(searchString.length >= 2 ? (new RegExp(this.str2re(searchString), 'i')) : null);
            }
        });

        // Subscribe to items modification events
        this._items.changes.pipe(
            startWith(null),
            takeUntil(this._onDestroy)
        ).subscribe(() => {
            this._updateSelectionFromModel();  // before _updateDisplayState
            this._updateItemsVisibility();  // last because redraw inside
            // console.log('Items updated', this._selection, this._selection ? this._selection.selected : '');
            this.isActive && this.redraw();

            // (Re)subscribe to items' (de)selection events
            merge(...this._items.map(item => item.onSelectionStateChange))
                .pipe(takeUntil(merge(this._items.changes, this._onDestroy)))
                .subscribe((event : DropdownOptionSelectionStateChangeEvent) => {
                    this.onItemSelectionStateChange(event);
                });
        });

        // console.log('--- INIT DONE ---');
    }

    // Bindings & listeners
    // -------------------------

    // On item click
    public onItemSelectionStateChange (event : DropdownOptionSelectionStateChangeEvent) : void {
        const { item } = event;

        item.selected ? this._selectItem(item) : this._deselectItem(item);
        this._updateDisplayState();

        if (this._multiple) {
            this._search && this.elSearchInput && this.elSearchInput.nativeElement.focus();
        } else {
            this.deactivate();
        }
        // console.log('Item (de)selected', event);
    }

    public onSearchInput () : void {
        this.searchSubject.next(this.searchString);
        this._updateDisplayState();
        // search by string
    }

    public _updateDisplayState () : void {
        this.displayText = '';
        this.displayType = 'html';
        this.displayStyle = 'hidden';
        this.displayTemplate = null;

        // console.log('_updateDisplayState', this._search, this.searchString);

        const selectedItem : DropdownItemComponent = this._multiple ? this._selection[0] : this._selection;
        const selectionLength : number = this._multiple ? this._selection.length : (this._selection ? 1 : 0);

        // TODO: i18n support
        // Selected items
        if (selectionLength && (!this.isActive || !this.searchString)) {
            this.displayStyle = this.isActive && this._search ? 'placeholder' : 'default';

            if (selectionLength > 1) {
                this.displayText = `<strong>${ selectionLength }</strong> options selected`;
            } else if (selectedItem.displayTemplate) {
                this.displayTemplate = selectedItem.displayTemplate;
                this.displayType = 'template';
            } else {
                this.displayText = selectedItem.display || selectedItem.value.toString();
            }

        // Placeholder
        } else if (this.placeholder && !selectionLength && (!this.isActive || !this.searchString)) {
            this.displayStyle = 'placeholder';
            this.displayText = this.placeholder;

        // Type to find
        } else if (!selectionLength && this.isActive && this._search && !this.searchString) {
            this.displayStyle = 'placeholder';
            this.displayText = 'Type to find...';
        }
    }

    public _applySearchRegexp (searchRegexp : RegExp) : void {
        this._searchRegexp = searchRegexp;
        this._updateItemsVisibility();
        this.isActive && this.redraw();
    }

    public _updateItemsVisibility () : void {
        if (!this._items) {
            return;
        }

        const re = this._searchRegexp;

        if (re) {
            let isListEmpty = true;

            this._itemGroups.forEach(group => group.hidden = true);

            this._items.forEach(item => {
                if (!(item.hidden = re ? !re.test(item.textContent) : false)) {
                    isListEmpty = false;
                    item.group && (item.group.hidden = false);
                }
            });

            this.empty = isListEmpty;
        } else {
            this._items.forEach(item => {
                item.hidden = false;
                item.group && (item.group.hidden = false);
            });

            this.empty = false;
        }
    }

    // TODO: move to service
    public str2re (source : string) : string {
        source = source.replace(/\s+/g, ' ');

        let result : string = '';

        for (let i = 0, len = source.length; i < len; ++i) {
            const charCode = source[i].charCodeAt(0);
            result += charCode == 32 ? '\\s+' : ('\\u' + ('000' + charCode.toString(16)).slice(-4));
        }

        return result;
    }

    public onDisplayClick (e : any) : void {
        if (this.domService.hasEventMark(e, 'dropdownSearchClick') || !this.isActive) {
            this.activate();
        } else {
            this.deactivate();
        }
    }

    public onSearchClick (e : any) : void {
        this.domService.markEvent(e, 'dropdownSearchClick');
    }

    /*
    @HostBinding('class')
    public get hostClasses () : string {
        const classes = [
            'dropdown',
            `dropdown_${ this._multiple ? 'multiple' : 'single' }`
        ];

        this._isTouch && classes.push('dropdown_touch');

        if (this._disabled) {
            classes.push('dropdown_disabled');
        } else if (this.isActive) {
            this.debug.assert(this.anchorPoint, '[Dropdown] Anchor point must not be empty when dropdown is active');
            classes.push('dropdown_active');
            classes.push(`dropdown_anchor_${ this.anchorPoint }`);
            this.isWider && classes.push('dropdown_dropdown-wider');
            this.empty && classes.push('dropdown_empty');
        }

        return classes.join(' ');
    }
    */

    @HostListener('document:click', [ '$event' ])
    public onRootClick (e : any) : void {
        // console.log('click');
        if (!this.domService.hasEventMark(e, 'dropdownClick')) {
            this.deactivate();
        }
    }

    @HostListener('click', [ '$event' ])
    public onHostClick (e : any) : void {
        // Disable label-click focus
        e.preventDefault();
        this.domService.markEvent(e, 'dropdownClick');
    }

    // TODO: use throttled events from DomService
    @HostListener('window:scroll')
    @HostListener('window:resize')
    public onDocumentReflow () : void {
        this.deactivate();
    }

    public reset () {
        if (!this._items) {
            return;
        }

        let defaultItem : DropdownItemComponent;

        if (this._items.length) {
            this._items.forEach(item => {
                if ((item.selected = item.default && !defaultItem)) {
                    defaultItem = item;
                }
            });

            if (!defaultItem && this._useFirstAsDefault) {
                defaultItem = this._items[0];
                defaultItem.selected;
            }
        }

        this._selection = this._multiple ? (defaultItem ? [ defaultItem ] : []) : defaultItem;
        // TODO: notify?
    }

    // update this.value (model) -> view & this._selection
    // --------------------------+
    // this.writeValue()         |
    // this.ngAfterContentInit() | -> this._updateSelectionFromModel()
    // --------------------------+
    public _updateSelectionFromModel () : void {
        // console.log('--- _updateSelectionFromModel', !!this._items);
        if (!this._items) {
            return;
        }

        const model = this._model;  // shortcut

        if (this._multiple) {
            const valueItemsLength = model.length;

            this._selection = this._items.filter(item => {
                for (let i = 0; i <= valueItemsLength; i++) {
                    if ((item.selected = item.value === model[i])) {
                        return true;
                    }
                }
                return false;
            });
        } else {
            let isItemSelected : boolean = false;
            // console.log('--- _updateSelectionFromModel 22222', model);

            this._items.forEach(item => {
                if ((item.selected = item.value === model && !isItemSelected)) {
                    this._selection = item;
                    isItemSelected = true;
                    // console.log('SELECTED:', item, item.selected);
                }
            });
        }

        this._updateModelFromSelection(false);
        this._updateDisplayState();
    }

    public _updateModelFromSelection (notify : boolean = true) : void {
        if (this._multiple) {
            this._model = this._selection.map(item => item.value);
        } else {
            this._model = this._selection ? this._selection.value : undefined;
        }
        // console.log('_updateModelFromSelection:', this._model, this._model ? this._model.selected : '');
        notify && this.onChange(this._model);
    }

    public _selectItem (itemToSelect : DropdownItemComponent) : void {
        if (!this._items) {
            return;
        }

        if (itemToSelect.solo || !this._multiple) {
            this._items.forEach(item => item.selected = item === itemToSelect);
            this._selection = this._multiple ? [ itemToSelect ] : itemToSelect;

        } else if (!this._selection.includes(itemToSelect)) {
            this._selection = this._items.filter(item => {
                return (item.selected = (item === itemToSelect || item.selected && !item.solo && (
                    (!item.group || !item.group.solo) &&
                    (!itemToSelect.group || !itemToSelect.group.solo) ||
                    (itemToSelect.group === item.group)
                )));
            });
        }

        // console.log('_selectItem', this._selection);

        this._updateModelFromSelection();
    }

    public _deselectItem (itemToDeselect : DropdownItemComponent) : void {
        if (this._multiple) {
            if (this._selection.includes(itemToDeselect)) {
                this._selection = this._selection.filter(item => item !== itemToDeselect);
            }
        } else {
            this._selection = undefined;
        }

        this._updateModelFromSelection();
    }

    public redraw (callback? : any) : void {
        requestAnimationFrame(() => {
            const elDropdown = this.elDropdown.nativeElement;
            const elList = this.elList.nativeElement;
            const windowSize = this.deviceService.viewportClientSize;
            const displayRect = this.elDisplay.nativeElement.getBoundingClientRect();
            const displayWidth = displayRect.width;
            const freeSpaceTop = displayRect.top;
            const freeSpaceBottom = windowSize.y - displayRect.bottom;
            const freeSpaceLeft = displayRect.right;
            const freeSpaceRight = windowSize.x - displayRect.left;
            const listHeight = elList.offsetHeight;
            const listWidth = elList.offsetWidth;
            // calc only once on init
            const dropdownBorders = this._dropdownBordersWidth || (this._dropdownBordersWidth = {
                x: elDropdown.offsetWidth - this.elScroll.nativeElement.offsetWidth,
                y: elDropdown.offsetHeight - listHeight
            });
            const desiredHeight = Math.min(DROPDOWN_MAX_WIDTH, listHeight + dropdownBorders.y);

            let anchorPointY: string;
            let freeSpaceY: number;

            if (freeSpaceBottom >= desiredHeight || freeSpaceBottom > freeSpaceTop) {
                anchorPointY = 'bottom';
                freeSpaceY = freeSpaceBottom;
            } else {
                anchorPointY = 'top';
                freeSpaceY = freeSpaceTop;
            }

            const scrollbarWidth = (
                Math.min(freeSpaceY, desiredHeight) < (listHeight + dropdownBorders.y) ?
                    this.domService.scrollbarSize :
                    0
            );

            const desiredWidth = Math.min(DROPDOWN_MAX_HEIGHT, listWidth + dropdownBorders.x + scrollbarWidth);

            if (freeSpaceRight >= desiredWidth || freeSpaceRight > freeSpaceLeft) {
                this.anchorPoint = <AnchorPoint>(`${anchorPointY}-left`);
                this.dropdownWidth = Math.min(desiredWidth, freeSpaceRight);
            } else {
                this.anchorPoint = <AnchorPoint>(`${anchorPointY}-right`);
                this.dropdownWidth = Math.min(desiredWidth, freeSpaceLeft);
            }

            this.dropdownHeight = desiredHeight > freeSpaceY ? (freeSpaceY + 1) : desiredHeight;
            this.isListFullWidth = this.empty || listWidth < (displayWidth - dropdownBorders.x - scrollbarWidth);
            this.isWider = this.dropdownWidth > displayWidth;

            callback && callback();
        });
    }

    public activate () : void {
        if (this.isActive || this._disabled) {
            return;
        }

        this.redraw(() => {
            this.isActive = true;
            this._updateDisplayState();
            this._search && requestAnimationFrame(() => {
                this.elSearchInput && this.elSearchInput.nativeElement.focus();
            });
        });
    }

    public deactivate () : void {
        if (!this.isActive) {
            return;
        }

        this.isWider = false;
        this.anchorPoint = null;
        this.dropdownWidth = null;
        this.dropdownHeight = null;
        this.isListFullWidth = false;
        this.searchString = '';
        this.isActive = false;
        this._applySearchRegexp(null);
        this._updateDisplayState();
        this.onTouched();
    }

    // Implementation of ControlValueAccessor
    // --------------------------------------

    // Model -> View
    public writeValue (value : any) : void {
        // console.log('writeValue', value);
        this._model = this._multiple ? (Array.isArray(value) ? value : []) : value;
        this._updateSelectionFromModel();
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this._disabled = isDisabled;
    }
}
