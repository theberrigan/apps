import {
    AfterContentInit,
    ChangeDetectionStrategy, ChangeDetectorRef,
    Component,
    DoCheck, HostBinding, Input,
    OnChanges,
    OnInit,
    SimpleChanges,
    ViewEncapsulation
} from '@angular/core';
import {DomService} from '../../services/dom.service';

@Component({
    selector: 'dropdown-group',
    exportAs: 'dropdownGroup',
    templateUrl: './dropdown-group.component.html',
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.Default,
    providers: []
})
export class DropdownGroupComponent implements OnInit, DoCheck, OnChanges, AfterContentInit {
    // Options.disabled
    // ----------------------------

    public _disabled : boolean = false;

    @Input()
    public get disabled () : boolean {
        return this._disabled;
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


    // @ContentChildren(DropdownItemComponent)
    // public items : QueryList<DropdownItemComponent>;

    @HostBinding('class')
    public get hostClasses () : string {
        const classes = [ 'dropdown__menu-group' ];
        this.disabled && classes.push('dropdown__menu-group_disabled');
        return classes.join(' ');
    }

    @HostBinding('class.hidden')
    public hidden : boolean = false;

    constructor (
        private cdr : ChangeDetectorRef,
        private domService : DomService
    ) {}

    // Angular hooks
    // --------------------------------------

    public ngOnInit () : void {

    }

    public ngDoCheck () : void {
        // console.log('ngDoCheck');
    }

    public ngOnChanges (changes : SimpleChanges) : void {
        // if (changes.disabled) {
        //     this.updateItemsDisableState();
        // }
    }

    public ngAfterContentInit () : void {
        // this.updateItems();
        // this.items.changes.subscribe(() => this.updateItems());
    }

    // public updateItems () : void {
    //     if (!this.items) {
    //         return;
    //     }
    // }
}
