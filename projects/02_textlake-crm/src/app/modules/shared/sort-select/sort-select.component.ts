import {
    Component, forwardRef, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {cloneDeep, isArray} from 'lodash';

interface Sort {
    by : any;
    direction : number;
}

interface Option {
    display : string;
    value : any;
}

@Component({
    selector: 'sort-select',
    exportAs: 'sortSelect',
    templateUrl: './sort-select.component.html',
    styleUrls: [ './sort-select.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => SortSelectComponent),
            multi: true
        }
    ],
    host: {
        'class': 'sort-select',
    }
})
export class SortSelectComponent implements OnInit, OnDestroy, ControlValueAccessor {
    public by : any = null;
    public direction : number = null;

    public _isDisabled : boolean = false;

    @Input()
    public set isDisabled (isDisabled : boolean) {
        this._isDisabled = isDisabled;
    }

    public get isDisabled () : boolean {
        return this._isDisabled;
    }

    public _options : Option[] = [];

    @Input()
    public set options (options : Option[]) {
        this._options = options && isArray(options) ? cloneDeep(options) : [];
    }

    public get options () : Option[] {
        return this._options;
    }

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public writeValue (source : Sort) : void {
        source = source || {
            by: null,
            direction: null
        };

        this.by = source.by || null;
        this.direction = source.direction || null;
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this._isDisabled = isDisabled;
    }

    public onByChange (by : any) : void {
        if (this.by !== by) {
            this.by = by;
            if (this.direction !== 1 && this.direction !== -1) {
                this.direction = 1;
            }
            this.emitOnChange();
        }

        this.onTouched();
    }

    public onDirectionClick (direction : number) : void {
        if (this.direction !== direction) {
            this.direction = direction;
            if (!this.options.find(option => option.value === this.by) && this.options.length) {
                this.by = this.options[0].value;
            }
            this.emitOnChange();
        }

        this.onTouched();
    }

    public emitOnChange () : void {
        this.onChange({
            by: this.by,
            direction: this.direction
        });
    }
}




