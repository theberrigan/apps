import {
    Component, forwardRef, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {cloneDeep, isArray} from 'lodash';

type View = 'grid' | 'grid-detailed' | 'table';

@Component({
    selector: 'list-view',
    exportAs: 'listView',
    templateUrl: './list-view.component.html',
    styleUrls: [ './list-view.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => ListViewComponent),
            multi: true
        }
    ],
    host: {
        'class': 'list-view',
    }
})
export class ListViewComponent implements OnInit, OnDestroy, ControlValueAccessor {
    public view : View;

    public _isDisabled : boolean = false;

    @Input()
    public set isDisabled (isDisabled : boolean) {
        this._isDisabled = isDisabled;
    }

    public get isDisabled () : boolean {
        return this._isDisabled;
    }

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public writeValue (view : View) : void {
        this.view = view || null;
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

    public onClick (view : View) : void {
        if (this.view !== view) {
            this.view = view;
            this.onChange(view);
        }

        this.onTouched();
    }
}




