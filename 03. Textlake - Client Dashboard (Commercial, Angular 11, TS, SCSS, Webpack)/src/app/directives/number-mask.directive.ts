import {
    AfterViewInit, Directive, ElementRef, EventEmitter, forwardRef, Inject, Input,
    OnChanges, OnDestroy, OnInit, Optional, Output, Renderer2, SimpleChanges
} from '@angular/core';
import { COMPOSITION_BUFFER_MODE, ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import {
    defer, truncateFraction, toFixedFraction, getFractionLength, int, isInt, float,
    isFinite, formatNumber, insertToString, getSelectionRange, mulFloat, divFloat
} from '../lib/utils';

class Options {
    public readonly min : number | null = null;
    public readonly max : number | null = null;
    public readonly defaultValue : number | null = null;
    public readonly viewFraction : number = 1;
    public readonly updateOn : 'change' | 'blur' = 'change';
    public readonly emitEventOnUntouchedChanged : boolean = false;
    public readonly delimiter : string = ' ';
    public readonly allowZero : boolean = true;
    public readonly type : 'number' | 'float' | 'int' = 'number';
    public readonly fractionMin : number | null = null;
    public readonly fractionMax : number | null = null;
    public readonly fractionFixTo : number | null = null;
    public readonly sign : '-' | '+' | null = null;

    private readonly allowedCharCodes : number[] = [ 48, 49, 50, 51, 52, 53, 54, 55, 56, 57 ];  // 0-9
    private readonly regexp : RegExp | null = null;

    public constructor (options? : Options) {
        if (!options) {
            return;
        }

        // viewFraction
        if ('viewFraction' in options && options.viewFraction != null) {
            if (!isFinite(options.viewFraction)) {
                throw new Error(`'viewFraction' is incorrect: ${ options.viewFraction }`);
            }

            this.viewFraction = options.viewFraction;
        }

        // type
        if ('type' in options) {
            if ([ 'number', 'float', 'int' ].indexOf(options.type) === -1) {
                throw new Error(`'type' must be 'number', 'float' or 'int', but '${ options.type }' given.`);
            }

            this.type = options.type;
        }

        if (this.type == 'number' && (options.fractionFixTo != null || options.fractionMin != null)) {
            throw new Error(`'fractionFixTo' or 'fractionMin' aren't allowed together with 'type' == 'number'.`);
        }

        // fractionFixTo
        if ('fractionFixTo' in options && options.fractionFixTo != null) {
            if (this.type == 'int') {
                throw new Error(`'fractionFixTo' isn\'t allowed together with 'type' == 'int'.`);
            }

            if (!isFinite(options.fractionFixTo) || options.fractionFixTo < 1) {
                throw new Error(`'fractionFixTo' is incorrect: ${ options.fractionFixTo }`);
            }

            this.fractionFixTo = options.fractionFixTo;
        }

        // fractionMin
        if ('fractionMin' in options && options.fractionMin != null) {
            if (this.type != 'float') {
                throw new Error(`'fractionMin' isn\'t allowed together with 'type' == '${ this.type }'.`);
            }

            if (!isFinite(options.fractionMin) || options.fractionMin < 1) {
                throw new Error(`'fractionMin' is incorrect: ${ options.fractionMin }`);
            }

            this.fractionMin = options.fractionMin;
        }

        // fractionMax
        if ('fractionMax' in options && options.fractionMax != null) {
            if (this.type == 'int') {
                throw new Error(`'fractionMax' isn\'t allowed together with 'type' == 'int'.`);
            }

            if (!isFinite(options.fractionMax) || options.fractionMax < 1) {
                throw new Error(`'fractionMax' is incorrect: ${ options.fractionMax }`);
            }

            this.fractionMax = options.fractionMax;
        }

        if (this.fractionFixTo != null && (this.fractionMin != null || this.fractionMax != null)) {
            throw new Error(`'fractionFixTo' isn\'t allowed together with 'fractionMin' and/or 'fractionMax'.`);
        }

        if (this.fractionMin != null && this.fractionMax != null && this.fractionMin > this.fractionMax) {
            throw new Error(`'fractionMax' (${ options.fractionMax }) must be greater than or equal to 'fractionMin' (${ options.fractionMin }).`);
        }

        if (this.type == 'float' && this.fractionFixTo == null && this.fractionMin == null) {
            this.fractionMin = 1;
        }

        // sign
        if ('sign' in options) {
            if ([ null, '+', '-' ].indexOf(options.sign) === -1) {
                throw new Error(`'sign' must be null, '+' or '-', but '${ options.sign }' given.`);
            }

            this.sign = options.sign;
        }

        // allowZero
        if ('allowZero' in options) {
            if (typeof(options.allowZero) !== 'boolean') {
                throw new Error(`'allowZero' must be true or false, but '${ options.allowZero }' given.`);
            }

            this.allowZero = options.allowZero;
        }

        if (this.type != 'int') {  // .,
            this.allowedCharCodes.push(44, 46);
        }

        if (this.sign != '+') {  // -
            this.allowedCharCodes.push(45);
        }

        // min & max
        const
            hasMin : boolean = 'min' in options && options.min != null,
            hasMax : boolean = 'max' in options && options.max != null,
            min : number = options.min,
            max : number = options.max;

        if (hasMin && !isFinite(min)) {
            throw new Error(`'min' is incorrect: ${ min }`);
        }

        if (hasMax && !isFinite(max)) {
            throw new Error(`'max' is incorrect: ${ max }`);
        }

        if (hasMin && hasMax && min > max) {
            throw new Error(`'max' (${ max }) must be greater than 'min' (${ min })`);
        }

        if (
            this.sign == '+' && (hasMin && min < 0 || hasMax && max < 0) ||
            this.sign == '-' && (hasMin && min > 0 || hasMax && max > 0)
        ) {
            throw new Error(`'min' (${ min }) or 'max' (${ max }) doesn\'t match the 'sign' (${ this.sign }).`);
        }

        this.min = hasMin ? min : this.sign != '+' ? null : 0;
        this.max = hasMax ? max : this.sign != '-' ? null : 0;

        // defaultValue
        if ('defaultValue' in options && options.defaultValue != null) {
            if (!isFinite(options.defaultValue)) {
                throw new Error(`'defaultValue' is incorrect: ${ options.defaultValue }`);
            }

            if (options.defaultValue == 0 && !this.allowZero) {
                throw new Error(`According to the 'allowZero' == false the 'defaultValue' must be unequal to 0.`);
            }

            if (options.defaultValue < 0 && this.sign == '+') {
                throw new Error(`According to the 'sign' (${ this.sign }) the 'defaultValue' must be positive, but negative given: ${ options.defaultValue }`);
            }

            if (options.defaultValue > 0 && this.sign == '-') {
                throw new Error(`According to the 'sign' (${ this.sign }) the 'defaultValue' must be negative, but positive given: ${ options.defaultValue }`);
            }

            const viewValue : number = divFloat(options.defaultValue, this.viewFraction);

            if (this.type == 'int' && !isInt(viewValue)) {
                throw new Error(`According to the 'type' ('int') the 'defaultValue' must be integer, but float given: ${ viewValue }`);
            }

            if (hasMin && options.defaultValue < min) {
                throw new Error(`The 'defaultValue' (${ options.defaultValue }) must be greater than 'min' (${ min }).`);
            }

            if (hasMax && options.defaultValue > max) {
                throw new Error(`The 'defaultValue' (${ options.defaultValue }) must be less than 'max' (${ max }).`);
            }

            this.defaultValue = options.defaultValue;
        }

        // updateOn
        if ('updateOn' in options && options.updateOn != null) {
            if ([ 'change', 'blur' ].indexOf(options.updateOn) === -1) {
                throw new Error(`'updateOn' must 'change' or 'blur': ${ options.updateOn }`);
            }

            this.updateOn = options.updateOn;
        }

        // emitEventOnUntouchedChanged
        if ('emitEventOnUntouchedChanged' in options) {
            if (typeof(options.emitEventOnUntouchedChanged) !== 'boolean') {
                throw new Error(`'emitEventOnUntouchedChanged' must be 'true' or 'false', but '${ options.emitEventOnUntouchedChanged }' given.`);
            }

            this.emitEventOnUntouchedChanged = options.emitEventOnUntouchedChanged;
        }

        // emitEventOnUntouchedChanged
        if ('delimiter' in options) {
            if (options.delimiter == null) {
                this.delimiter = '';
            } else {
                if (typeof(options.delimiter) !== 'string') {
                    throw new Error(`'delimiter' must be of type string, but '${ options.delimiter }' given.`);
                }

                this.delimiter = options.delimiter;
            }
        }

        // regexp
        {
            const
                minus : string = this.sign != '+' ? this.sign != '-' ? '-?' : '-' : '',  // '-' | '-?' | ''
                minusGroup : string = this.sign != '+' ? '-|' : '',  // '-|' | ''
                zeroGroup : string = this.allowZero || this.type == 'float' && this.sign != '-' ? '0|' : '';  // '0|' | ''

            if (this.type == 'int') {
                this.regexp = new RegExp(`^(${ zeroGroup }${ minusGroup }${ minus }[1-9]\\d*)$`);
            } else {
                const
                    maxFractionLength : number = this.fractionFixTo || this.fractionMax,
                    fractionQuantifier : string = maxFractionLength ? `{0,${ maxFractionLength }}` : '*',  // '*' | '{0,X}'
                    fraction : string = `([.,]\\d${ fractionQuantifier })?`;  // '([.,]\d+)?' | '([.,]\d{0,X})?'

                this.regexp = new RegExp(`^(${ zeroGroup }${ minusGroup }${ minus }0${ fraction }|${ minus }[1-9]\\d*${ fraction })$`);
            }
        }
    }

    public isValidValue (value : string) : boolean {
        return !this.regexp || this.regexp.test(value);
    }

    public isValidCharCode (charCode : number) : boolean {
        return this.allowedCharCodes.indexOf(charCode) > -1;
    }
}

const optionsTemplates : {[ key : string ] : Options } = {};

@Directive({
    selector: `input[type='text'][number-mask]`,
    exportAs: 'numberModel',
    host: {
        '(keypress)': 'onKeypress($event)',
        '(input)': 'onInput($event)',
        '(cut)': 'onCut($event)',
        '(paste)': 'onPaste($event)',
        '(blur)': 'onFocusChanged($event)',
        '(focus)': 'onFocusChanged($event)',
        '(keydown)': 'onKeydown($event)',
        '(compositionstart)': 'onCompositionChange($event)',
        '(compositionend)': 'onCompositionChange($event)'
    },
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => NumberMaskDirective),
            multi: true
        }
    ]
})
export class NumberMaskDirective implements ControlValueAccessor, OnInit, AfterViewInit, OnChanges, OnDestroy {
    @Input('numberModel')
    public model : number;

    @Input('numberModelOptions')
    public modelOptions : Options | string;

    @Output('numberModelChange')
    public updateModelEvent : EventEmitter<any> = new EventEmitter<any>();

    public onChange : any = () => {};

    public onTouched : any = () => {};

    public options : Options = null;

    public isDisabled : boolean = false;

    public isTouched : boolean = false;

    public isFocused : boolean = false;

    public isDelete : boolean = false;

    public isPaste : boolean = false;

    public isCut : boolean = false;

    public isComposing : boolean = false;

    // ----------------

    public isCaretPositionSupported : boolean = true;

    public state : any = null;

    constructor (
        private el : ElementRef,
        private renderer : Renderer2
    ) {}

    // <LIFECYCLE_HOOKS>

    public ngOnInit () : void {
        // console.warn('ngOnInit(): updateOptions() => updateView()');
        this.state = {
            num: null,
            formatted: null,
            prevValue: null
        };

        this.updateOptions();
        this.updateView(this.model);
    }

    public ngAfterViewInit () : void {

    }

    public ngOnDestroy () : void {

    }

    // This hook fires when a parent component updates @Input()-props
    public ngOnChanges (changes : SimpleChanges) : void {
        // console.warn('ngOnChanges():', changes);

        if (changes.modelOptions && !changes.modelOptions.firstChange) {
            // console.warn('\tngOnChanges(): updateOptions()');
            this.updateOptions();
        }

        if (changes.model && !changes.model.firstChange && this.state.num !== changes.model.currentValue) {
            // console.warn('\tngOnChanges: updateView()');
            this.updateView(this.model);
        }
    }

    // </LIFECYCLE_HOOKS>

    // <CONTROL_VALUE_ACCESSOR_INTERFACE>

    public registerOnChange (fn : Function) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : Function) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this.el.nativeElement && this.renderer.setProperty(this.el.nativeElement, 'disabled', this.isDisabled = isDisabled);
    }

    public writeValue (value : number) : void {
        this.updateView(value);
    }

    public reset () : void {
        this.updateView(null);
    }
    public updateView (value : number) : void {
        defer(() => {
            if (this.isFocused) {
                return;
            }

            this.updateState({
                num: this.validateNumber(value, this.options.defaultValue),
                updateInput: true
            });
        });
    }

    public updateOptions () : void {
        const options : Options | string = this.modelOptions;

        if (typeof(options) === 'string') {
            if (options in optionsTemplates) {
                this.options = optionsTemplates[options];
            } else {
                throw new Error(`Unknown options template key: ${ options }.`);
            }
        } else {
            this.options = new Options(options);
        }
    }

    public updateState (state : {
        num? : number,
        reformat? : boolean,
        updateInput? : boolean,
        prevValue? : string,
        isBlur? : boolean
    }) : void {
        const
            num : number = 'num' in state ? state.num : this.state.num,
            formatted : string = 'num' in state || state.reformat ? this.formatNumber(num) : this.state.formatted,
            prevValue : string = state.updateInput ? formatted : 'prevValue' in state ? state.prevValue : this.state.prevValue;

        this.state = { num, formatted, prevValue };

        if (state.updateInput) {
            this.inputValue = formatted || '';
        }

        if (
            this.model !== num && (
                !this.isTouched && this.options.emitEventOnUntouchedChanged ||
                this.options.updateOn == 'change' ||
                this.options.updateOn == 'blur' && state.isBlur
            )
        ) {
            // console.warn('UPDATE MODEL!');
            this.updateModelEvent.emit(num);
            this.onChange(num);
        }
    }

    public validateNumber (num : number, defaultValue : number = null) : number {
        if (
            !isFinite(num) ||
            !this.options.allowZero && num === 0 ||
            this.options.sign == '+' && num < 0 ||
            this.options.sign == '-' && num > 0
        ) {
            num = defaultValue;
        } else if (this.options.min != null && num < this.options.min) {
            num = this.options.min;
        } else if (this.options.max != null && num > this.options.max) {
            num = this.options.max;
        }

        if (num != null) {
            if (this.options.type == 'int') {
                num = int(num);
            } else {
                const fraction : number = this.options.fractionMax || this.options.fractionFixTo;

                if (fraction) {
                    num = mulFloat(truncateFraction(divFloat(num, this.options.viewFraction), fraction), this.options.viewFraction);
                }
            }
        }

        return num;
    }

    // Форматирует число в строку, которую можно вставить в поле ввода
    public formatNumber (num : number) : string {
        if (!isFinite(num)) {
            return null;
        }

        num = divFloat(num, this.options.viewFraction);

        let value : string = '';

        // Integer
        if (this.options.type == 'int') {
            value = String(int(num));

        // Number
        } else if (this.options.type == 'number') {
            value = String(num);

        } else if (this.options.fractionFixTo) {
            value = toFixedFraction(num, this.options.fractionFixTo);
        } else {
            const fraction : number = getFractionLength(num);

            if (this.options.fractionMin && fraction <= this.options.fractionMin) {
                value = num.toFixed(this.options.fractionMin);
            } else if (this.options.fractionMax && fraction >= this.options.fractionMax) {
                value = toFixedFraction(num, this.options.fractionMax);
            } else {
                value = String(num);
            }
        }

        if (!this.isFocused && this.options.delimiter) {
            value = formatNumber(value, this.options.delimiter);
        }

        return value;
    }


    public set inputValue (value : string) {
        this.el.nativeElement && this.renderer.setProperty(this.el.nativeElement, 'value', String(value).trim());
    }

    public get inputValue () : string {
        return (this.el.nativeElement || { value: '' }).value.trim();
    }

    public onKeydown (e : any) : void {
        this.isDelete = (
            e.keyCode == 8  || e.code == 'Backspace' || e.key == 'Backspace' ||
            e.keyCode == 46 || e.code == 'Delete'    || e.key == 'Delete'
        );
    }

    public onKeypress (e : any) : void {
        const charCode : number = e.which || e.charCode || e.keyCode;

        // console.log('onKeypress:', charCode, String.fromCharCode(charCode));

        if (e.metaKey || e.ctrlKey || e.which < 32 || [ 8, 46, 36, 35, 37, 38, 39, 40 ].indexOf(e.which) !== -1) {
            return;
        }

        // Запретить ввод недопустимых символов
        if (!this.options.isValidCharCode(charCode)) {
            e.preventDefault();
            return;
        }

        if (!this.isCaretPositionSupported) {
            return;
        }

        const
            input : HTMLInputElement = this.el.nativeElement || e.target,
            selection : any = getSelectionRange(input);

        if (!selection) {
            this.isCaretPositionSupported = false;
            return;
        }

        let value : string = insertToString(input.value, String.fromCharCode(charCode), selection.start, selection.end);

        // Отменить событие, если значение содержит допустимые символы, но всё равно не валидно
        if (value && !this.options.isValidValue(value)) {
            e.preventDefault();
        }
    }

    public onInput (e : any) : void {
        const
            input : HTMLInputElement = this.el.nativeElement || e.target,
            value : string = input.value.replace(/[\r\t\n\s]+/g, '').replace(/,/g, '.'),
            inputType : string = (e.inputType || '').toLowerCase(),
            isPaste : boolean = this.isPaste || inputType.indexOf('paste') !== -1,
            isCut  : boolean = this.isCut || inputType.indexOf('bycut') !== -1,
            isDelete : boolean = !isPaste && !isCut && (this.isDelete || inputType.indexOf('delete') === 0),
            isTyped : boolean = (
                !isDelete && !isPaste && !isCut &&
                ((value.length - (this.state.prevValue || '').length) > 0 || inputType.indexOf('insert') === 0)
            );

        let num : number = this.validateNumber(mulFloat(float(value), this.options.viewFraction)),
            updateInput : boolean = isPaste;  // После вставки всегда нужно обновить поле ввода

        if (num == null) {
            if (isPaste || isCut || isDelete) {
                num = this.options.defaultValue;
            } else if (isTyped) {
                num = this.state.num != null ? this.state.num : this.options.defaultValue;
                updateInput = !this.options.isValidValue(value);  // not safe insert
            }
        }

        this.updateState({
            num,
            updateInput,
            prevValue: value
        });

        this.isDelete = this.isCut = this.isPaste = false;
    }

    public onPaste () : void {
        this.isPaste = true;
    }

    public onCut () : void {
        this.isCut = true;
    }

    public onFocusChanged (e : any) : void {
        // console.log('onFocusChanged:', e.type);
        this.isFocused = e.type == 'focus';
        this.isTouched = true;

        this.updateState({
            reformat: true,
            updateInput: true,
            isBlur: !this.isFocused
        });

        if (!this.isFocused) {
            this.onTouched();
        }
    }

    public onCompositionChange (e : any) : void {
        if (!(this.isComposing = (e.type == 'compositionstart'))) {
            this.isPaste = true;
            this.onInput(e);
        }
    }
}
