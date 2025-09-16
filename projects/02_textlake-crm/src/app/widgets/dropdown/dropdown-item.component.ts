import {
    AfterContentInit,
    ChangeDetectionStrategy, ChangeDetectorRef,
    Component, ContentChild, ContentChildren,
    DoCheck, ElementRef, EventEmitter, forwardRef, Host, HostBinding, HostListener, Inject, InjectionToken, Input,
    OnChanges,
    OnInit, Optional, Output, QueryList, SimpleChanges, TemplateRef, ViewChild, ViewContainerRef,
    ViewEncapsulation
} from '@angular/core';
import {DropdownGroupComponent} from './dropdown-group.component';
import {DomService} from '../../services/dom.service';
import {DropdownComponent} from './dropdown.component';

// export interface DropdownItemParentComponent {
//     disabled : boolean;
// }


export class DropdownOptionSelectionStateChangeEvent {
    constructor (
        public item : DropdownItemComponent,
        public byUser : boolean
    ) {}
}

@Component({
    selector: 'dropdown-item',
    exportAs: 'dropdownItem',
    templateUrl: './dropdown-item.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.Default
})
export class DropdownItemComponent implements OnInit, DoCheck, OnChanges, AfterContentInit {
    // Options.display
    // ----------------------------

    public _display : string = '';

    @Input()
    public get display () : string {
        return this._display;
    }

    public set display (value : string) {
        this._display = String(value || '').trim();
    }

    // Options.disabled
    // ----------------------------

    public _disabled : boolean = false;

    @Input()
    public get disabled () : boolean {
        return this._disabled || this.group && this.group.disabled || this.dropdown.disabled;
    }

    public set disabled (value : boolean) {
        this._disabled = this.domService.parseBooleanAttr(value);
    };

    // Options.solo
    // ----------------------------

    public _solo : boolean = false;

    @Input()
    public get solo () : boolean {
        return this._solo;
    }

    public set solo (value : boolean) {
        this._solo = this.domService.parseBooleanAttr(value);
    };

    // Options.default
    // ----------------------------

    public _default : boolean = false;

    @Input()
    public get default () : boolean {
        return this._default;
    }

    public set default (value : boolean) {
        this._default = this.domService.parseBooleanAttr(value);
    };

    // Options.value
    // ----------------------------

    @Input()
    public value : any;

    public _selected : boolean = false;

    @Input()
    public get selected () : boolean {
        return this._selected;
    }

    public set selected (value : boolean) {
        this._selected = value;
    };

    @Output()
    public readonly onSelectionStateChange = new EventEmitter<DropdownOptionSelectionStateChangeEvent>();

    @ContentChild(TemplateRef)
    public displayTemplate : TemplateRef<any>;

    @Output()
    public get textContent () : string {
        return this.itemContent && this.itemContent.nativeElement.textContent || '';
    }

    @HostBinding('class.hidden')
    public hidden : boolean = false;

    constructor (
        // @Inject(DROPDOWN_GROUP_COMPONENT)
        // public group : DropdownGroupComponent,
        @Optional()
        @Inject(forwardRef(() => DropdownGroupComponent))
        public group : DropdownGroupComponent,
        @Inject(forwardRef(() => DropdownComponent))
        private dropdown : DropdownComponent,
        private cdr : ChangeDetectorRef,
        private domService : DomService
    ) {}

    @HostBinding('class')
    public get hostClasses () : string {
        // if (this.value === 'AO') {
        //     console.log('---> hostClasses', this.selected);
        // }
        const classes = [ 'dropdown__menu-item' ];
        this.selected && classes.push('dropdown__menu-item_selected');
        this.disabled && classes.push('dropdown__menu-item_disabled');
        return classes.join(' ');
    }

    @ViewChild('itemContent')
    public itemContent : ElementRef;

    @HostListener('click')
    public _onHostClick () : void {
        if (!this.disabled) {
            this.selected = this.dropdown.multiple ? !this.selected : true;
            this._onSelectionStateChange(true);
        }
    }

    public _onSelectionStateChange (byUser : boolean = false) : void {
        this.onSelectionStateChange.emit(new DropdownOptionSelectionStateChangeEvent(this, byUser));
    }

    // Angular hooks
    // --------------------------------------

    public ngOnInit () : void {
        // console.log('Item created, group:', !!this.group, 'dropdown:', !!this.dropdown, 'multiple:', this.dropdown.multiple);
    }

    public ngDoCheck () : void {

    }

    public ngOnChanges (changes : SimpleChanges) : void {

    }

    public ngAfterContentInit () {

    }
}
