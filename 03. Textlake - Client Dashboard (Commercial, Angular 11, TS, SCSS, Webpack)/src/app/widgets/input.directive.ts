import {
    Directive, ElementRef, EventEmitter, forwardRef, Input, OnDestroy,
    OnInit, Renderer2,
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';

@Directive({
    // TODO; change
    selector: '[input-mask]',
    exportAs: 'inputMask',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => InputDirective),
            multi: true
        }
    ],
    host: {

    }
})
export class InputDirective implements OnInit, OnDestroy, ControlValueAccessor {
    @Input()
    public set isDisabled (isDisabled : boolean) {
        this.el && (this.el.nativeElement.disabled = isDisabled);
    }

    public get isDisabled () : boolean {
        return this.el && this.el.nativeElement.disabled;
    }

    @Input()
    public valueType : 'number' | 'text' = 'text';

    public value : string = null;

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor (
        public el : ElementRef,
        public renderer : Renderer2
    ) {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public writeValue (value : any) : void {
        // TODO: change
        this.value = value;
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this.isDisabled = isDisabled;
    }

    // ---------------------
}
