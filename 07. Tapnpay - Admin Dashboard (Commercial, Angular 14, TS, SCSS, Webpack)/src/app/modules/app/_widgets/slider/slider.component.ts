import {
    Component,
    ElementRef,
    forwardRef,
    HostBinding,
    HostListener,
    Input,
    OnChanges,
    OnInit,
    Renderer2,
    SimpleChanges,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {clamp} from '../../../../lib/utils';

const BODY_DRAG_CLASS = 'slider-dragging';

@Component({
    selector: 'slider',
    exportAs: 'slider',
    templateUrl: './slider.component.html',
    styleUrls: [ './slider.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'slider'
    },
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => SliderComponent),
            multi: true
        }
    ],
})
export class SliderComponent implements OnInit, OnChanges, ControlValueAccessor {
    onTouched : any = () => {};

    onChange : any = (_ : null | number) => void {};

    fillWidth : number = 0;

    isActive : boolean = false;

    listeners : any[] = null;

    cursorState : number = null;

    @Input()
    steps : number = null;

    @Input()
    minValue : number = 0;

    @Input()
    maxValue : number = 1;

    @Input()
    isInteger : boolean = false;

    @Input()
    @HostBinding('class.slider_disabled')
    isDisabled : boolean = false;

    @ViewChild('contentEl')
    contentEl : ElementRef<HTMLDivElement>;

    constructor (
        public hostEl : ElementRef,
        public renderer : Renderer2,
    ) {}

    ngOnInit () {
        console.log('ngOnInit');
    }

    ngOnChanges (changes : SimpleChanges) {
        console.log('ngOnChanges', changes);
    }

    @HostListener('blur')
    onBlur () {
        if (this.onTouched) {
            this.onTouched();
        }
    }

    checkDisabled () : boolean {
        return this.isDisabled || !!this.hostEl?.nativeElement.closest('fieldset:disabled');
    }

    writeValue (value : number) {
        if (typeof value !== 'number') {
            this.fillWidth = 0;
            return;
        }

        if (this.isInteger) {
            value = Math.round(value);
        }

        const min = this.minValue;
        const max = this.maxValue;
        const percent = (value - min) / (max - min) * 100;

        this.fillWidth = clamp(percent, 0, 100);
    }

    registerOnChange (fn : any) {
        this.onChange = fn;
    }

    registerOnTouched (fn : any) {
        this.onTouched = fn;
    }

    setDisabledState (isDisabled : boolean) {
        this.isDisabled = !!isDisabled;
    }

    // -------------------------------------------

    @HostListener('mousedown', [ '$event' ])
    onHostMouseDown (e : MouseEvent) {
        if (this.checkDisabled()) {
            return;
        }

        this.cursorState = null;
        this.renderer.addClass(document.body, BODY_DRAG_CLASS);
        this.listeners = [
            this.renderer.listen(document.documentElement, 'mouseup', () => this.onDocMouseUp()),
            this.renderer.listen(document.documentElement, 'mousemove', e => this.processEvent(e)),
        ];

        this.processEvent(e);
    }

    onDocMouseUp () {
        this.renderer.removeClass(document.body, BODY_DRAG_CLASS);
        this.listeners.forEach(unlisten => unlisten());
        this.listeners = null;
    }

    processEvent (e : MouseEvent) {
        if (!this.contentEl) {
            return;
        }

        const contentEl = <HTMLDivElement>this.contentEl.nativeElement;
        const { left, right, width } = contentEl.getBoundingClientRect();
        const { clientX } = e;
        const ltMin = clientX < left;
        const gtMax = clientX > right;

        if (ltMin && this.cursorState === -1 || gtMax && this.cursorState === 1) {
            return;
        }

        this.cursorState = ltMin ? -1 : (gtMax ? 1 : 0);

        const cursorX = clamp(clientX, left, right) - left;
        const factor = this.normalizeFactor(cursorX / width, this.steps);
        const min = this.minValue;

        let value = min + ((this.maxValue - min) * factor);

        if (this.isInteger) {
            value = Math.round(value);
        }

        this.onChange(value);

        this.fillWidth = factor * 100;
    }

    private normalizeFactor (factor : number, steps : number = null) : number {
        if (typeof steps === 'number') {
            factor = 1 / (steps - 1) * Math.round((steps - 1) * factor);
        }

        return clamp(factor, 0, 1);
    }
}
