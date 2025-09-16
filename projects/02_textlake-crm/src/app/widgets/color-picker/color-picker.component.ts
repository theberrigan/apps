import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    forwardRef, HostBinding,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {DomService} from '../../services/dom.service';
import {ColorService} from '../../services/color.service';
import {isObject} from '../../lib/utils';

class ColorValue {
    bg : string;
    text : string;
}

const PALETTE_HEIGHT = 200;
const HUE_WIDTH = 32;
const SV_WIDTH = PALETTE_HEIGHT;
const SPACING = 14;

enum PopupState {
    Hidden = 0,
    Init = 1,
    Visible = 3
}

let instancesCounter = 0;

@Component({
    selector: 'color-picker',
    exportAs: 'colorPicker',
    templateUrl: './color-picker.component.html',
    styleUrls: [ './color-picker.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    // changeDetection: ChangeDetectionStrategy.OnPush,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => ColorPickerComponent),
            multi: true
        }
    ],
    host: {
        'class': 'color-picker'
    }
})
export class ColorPickerComponent implements OnInit, OnDestroy, ControlValueAccessor {
    @ViewChild('canvas')
    public canvas;

    @HostBinding('class.color-picker_disabled')
    public isDisabled : boolean = false;

    public value : ColorValue;

    public readonly canvasHeight : number = SPACING + PALETTE_HEIGHT + SPACING;

    public readonly canvasWidth : number = SPACING + SV_WIDTH + SPACING + HUE_WIDTH + SPACING;

    public readonly svBox : number[] = [
        SPACING,
        SPACING,
        SPACING + SV_WIDTH,
        SPACING + PALETTE_HEIGHT,
    ];

    public readonly hueBox : number[] = [
        SPACING + SV_WIDTH + SPACING,
        SPACING,
        SPACING + SV_WIDTH + SPACING + HUE_WIDTH,
        SPACING + PALETTE_HEIGHT,
    ];

    public readonly id : string;

    public popupState : PopupState = PopupState.Hidden;

    public popupStateEnum = PopupState;

    public isMouseDownWasOnPopup : boolean = false;

    public isMouseUpWasOnPopup : boolean = false;

    public isMouseDownWasOnDisplay : boolean = false;

    public wasDisplayClick : boolean = false;

    public canvasCtx : CanvasRenderingContext2D;

    public canvasEl : HTMLCanvasElement;

    public readonly hueColors : string[] = [
        '#ff0000',
        '#ffff00',
        '#00ff00',
        '#00ffff',
        '#0000ff',
        '#ff00ff',
        '#ff0000',
    ];

    public imageBase : ImageData;

    public imageWithHueHandleAndSV : ImageData;

    public colorPickArea : 'sv' | 'hue';

    public hueHandlerY : number = 0;

    public svHandlerX : number = 0;

    public svHandlerY : number = 0;

    public hueColor : string = '#ff0000';

    public unlistenCallbacks : any[] = [];

    public unlistenPopupCallbacks : any[] = [];

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor (
        public renderer : Renderer2,
        public hostEl : ElementRef,
        public domService : DomService,
        public colorService : ColorService
    ) {
        this.id = String(instancesCounter++);
    }

    public ngOnInit () : void {
        this.unlistenCallbacks.push(this.renderer.listen(document.documentElement, 'mouseup', e => this.onDocumentMouseUp(e)));
    }

    public ngOnDestroy () : void {
        this.destroyPopup();
        this.unlistenCallbacks.forEach(unlisten => unlisten());
    }

    public onDisplayMouseDown () : void {
        this.isMouseDownWasOnDisplay = true;
    }

    public onDisplayMouseUp () : void {
        if (this.isMouseDownWasOnDisplay) {
            this.setPopupState(this.popupState === PopupState.Hidden ? PopupState.Init : PopupState.Hidden);
            this.onTouched();
            this.wasDisplayClick = true;
        }
    }

    public setPopupState (state : PopupState) : void {
        this.popupState = state;

        if (this.popupState === PopupState.Init) {
            requestAnimationFrame(() => this.initPopup());
        } else if (this.popupState === PopupState.Hidden) {
            this.destroyPopup();
        }
    }

    public initPopup () : void {
        this.canvasEl = this.canvas.nativeElement;
        this.canvasCtx = this.canvasEl.getContext('2d');

        const [ svPosX, svPosY ] = this.svBox;

        this.canvasCtx.fillStyle = '#000';
        this.canvasCtx.fillRect(svPosX - 1, svPosY - 1, PALETTE_HEIGHT + 2, PALETTE_HEIGHT + 2);

        const [ huePosX, huePosY, _, huePosY2 ] = this.hueBox;

        // Border around hue
        this.canvasCtx.fillStyle = '#000';
        this.canvasCtx.fillRect(huePosX - 1, huePosY - 1, HUE_WIDTH + 2, PALETTE_HEIGHT + 2);

        // Hue gradient
        const gradient : any = this.canvasCtx.createLinearGradient(huePosX, huePosY, huePosX, huePosY2);
        this.hueColors.forEach((color, i) => gradient.addColorStop(1 / (this.hueColors.length - 1) * i, color));
        this.canvasCtx.fillStyle = gradient;
        this.canvasCtx.fillRect(huePosX, huePosY, HUE_WIDTH, PALETTE_HEIGHT);

        this.imageBase = this.canvasCtx.getImageData(0, 0, this.canvasWidth, this.canvasHeight);

        this.unlistenPopupCallbacks.push(this.renderer.listen(document.documentElement, 'mousemove', e => this.onCanvasMouseMove(e)));

        const hsv : number[] = this.colorService.hex2hsv(this.value.bg);

        this.hueHandlerY = this.hueBox[1] + Math.round(PALETTE_HEIGHT / 360 * hsv[0]);   // hsv[0]: 0 -> 360
        this.svHandlerX = this.svBox[0] + Math.round(SV_WIDTH * hsv[1]);                // hsv[1]: 0 -> 1
        this.svHandlerY = this.svBox[1] + Math.round(PALETTE_HEIGHT * (1 - hsv[2]));    // hsv[2]: 1 -> 0

        this.pickHue();
        this.drawSaturationValue();
        this.pickColor();
        this.drawHueHandle();
        this.imageWithHueHandleAndSV = this.canvasCtx.getImageData(0, 0, this.canvasWidth, this.canvasHeight);
        this.drawSVHandle();

        this.setPopupState(PopupState.Visible);

        // change hue -> imageBase -> pick hue -> draw sv -> pick sv -> draw hue handle -> save to imageWithHueHandleAndSV -> draw sv handle
        // change sv -> imageWithHueHandleAndSV -> pick sv -> draw sv handle
    }

    public destroyPopup () : void {
        if (this.popupState !== PopupState.Hidden) {
            this.setPopupState(PopupState.Hidden);
            return;
        }

        this.canvasCtx = null;
        this.unlistenPopupCallbacks.forEach(unlisten => unlisten());
        this.unlistenPopupCallbacks = [];
    }

    public pickHue () : void {
        this.hueColor = '#' + this.colorService.rgb2hex(this.canvasCtx.getImageData(this.hueBox[0], this.hueHandlerY, 1, 1).data);
    }

    public drawSaturationValue () : void {
        const ctx = this.canvasCtx;

        const [ svPosX, svPosY, svPosX2, svPosY2 ] = this.svBox;

        // Hue
        ctx.beginPath();
        ctx.rect(svPosX, svPosY, SV_WIDTH, PALETTE_HEIGHT);
        ctx.fillStyle = this.hueColor;
        ctx.fill();

        // Value
        const valueGradient = ctx.createLinearGradient(svPosX, svPosY, svPosX2, svPosY); // —
        valueGradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
        valueGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = valueGradient;
        this.canvasCtx.fillRect(svPosX, svPosY, PALETTE_HEIGHT, PALETTE_HEIGHT);

        // Saturation
        const saturationGradient = ctx.createLinearGradient(svPosX, svPosY, svPosX, svPosY2); // |
        saturationGradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
        saturationGradient.addColorStop(1, 'rgba(0, 0, 0, 1)');
        ctx.fillStyle = saturationGradient;
        this.canvasCtx.fillRect(svPosX, svPosY, PALETTE_HEIGHT, PALETTE_HEIGHT);
    }

    public pickColor () : void {
        const ctx = this.canvasCtx;
        const rgb = ctx.getImageData(this.svHandlerX, this.svHandlerY, 1, 1).data;
        this.value = {
            bg: '#' + this.colorService.rgb2hex(rgb),
            text: this.colorService.getContrastingColor([ ...rgb ])
        };
        this.onChange(this.value);
    }

    public drawHueHandle () : void {
        const ctx = this.canvasCtx;
        const baseX = this.hueBox[0];
        const baseY = this.hueHandlerY;
        const radius = 4;

        ctx.beginPath();
        ctx.arc(baseX, baseY, radius, Math.PI / 2, Math.PI / 2 * 3, false);
        ctx.lineTo(this.hueBox[2], baseY - radius);
        ctx.arc(this.hueBox[2], baseY, radius, Math.PI / 2 * 3, Math.PI / 2 * 5, false);
        ctx.lineTo(baseX, baseY + radius);
        ctx.fillStyle = this.hueColor;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#000';
        ctx.stroke();
        ctx.closePath();
    }

    public drawSVHandle () : void {
        const ctx = this.canvasCtx;

        ctx.beginPath();
        ctx.arc(this.svHandlerX, this.svHandlerY, 5, 0, 2 * Math.PI, false);
        ctx.fillStyle = this.value.bg;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = this.value.text;
        ctx.stroke();
        ctx.closePath();
    }

    public isPointInRect (pointX : number, pointY : number, rect : number[]) {
        return pointX >= rect[0] && pointY >= rect[1] && pointX <= rect[2] && pointY <= rect[3];
    }

    public onCanvasMouseDown (e : any) : void {
        const canvasRect = this.canvasEl.getBoundingClientRect();
        const canvasX = e.clientX - canvasRect.left;
        const canvasY = e.clientY - canvasRect.top;

        this.colorPickArea = (
            this.isPointInRect(canvasX, canvasY, this.svBox) ?
            'sv' :
            this.isPointInRect(canvasX, canvasY, this.hueBox) ?
            'hue' :
            null
        );

        if (this.colorPickArea) {
            this.renderer.addClass(document.body, 'body_color-picker-active');
            this.onCanvasMouseMove(e, canvasRect);
        }
    }

    public onCanvasMouseMove (e : any, canvasRect? : ClientRect) {
        if (!this.colorPickArea) {
            return;
        }

        canvasRect = canvasRect || this.canvasEl.getBoundingClientRect();

        const canvasX = e.clientX - canvasRect.left;
        const canvasY = e.clientY - canvasRect.top;

        if (this.colorPickArea === 'sv') {
            const box = this.svBox;
            this.svHandlerX = Math.max(box[0], Math.min(box[2] - 1, canvasX));
            this.svHandlerY = Math.max(box[1], Math.min(box[3] - 1, canvasY));

            this.canvasCtx.putImageData(this.imageWithHueHandleAndSV, 0, 0);

            this.pickColor();
            this.drawSVHandle();
        } else if (this.colorPickArea === 'hue') {
            const box = this.hueBox;
            this.hueHandlerY = Math.max(box[1], Math.min(box[3] - 1, canvasY));

            this.canvasCtx.putImageData(this.imageBase, 0, 0);

            this.pickHue();
            this.drawSaturationValue();
            this.pickColor();
            this.drawHueHandle();
            this.imageWithHueHandleAndSV = this.canvasCtx.getImageData(0, 0, this.canvasWidth, this.canvasHeight);
            this.drawSVHandle();
        }
    }

    public cancelColorPickArea () : void {
        this.colorPickArea = null;
        this.renderer.removeClass(document.body, 'body_color-picker-active');
    }

    // ----------------

    public onPopupMouseDown () : void {
        this.isMouseDownWasOnPopup = true;
    }

    public onPopupMouseUp () : void {
        this.isMouseUpWasOnPopup = true;
    }

    public onDocumentMouseUp (e : any) : void {
        if (!this.wasDisplayClick && !this.isMouseDownWasOnDisplay && !this.isMouseDownWasOnPopup) {
            this.setPopupState(PopupState.Hidden);
        }

        this.wasDisplayClick = false;
        this.isMouseDownWasOnDisplay = false;
        this.isMouseDownWasOnPopup = false;

        if (this.colorPickArea) {
            this.cancelColorPickArea();
        }
    }

    // ----------------------------------------

    public writeValue (value : ColorValue) : void {
        if (!value || !isObject(value)) {
            this.value = {
                bg: '#fff',
                text: '#000'
            };
        } else {
            value = Object.assign({}, value);

            if (typeof(value.bg) !== 'string') {
                value.bg = '#fff';
            }

            if (typeof(value.text) !== 'string') {
                value.bg = '#000';
            }

            this.value = value;
        }
        // console.log('writeValue', value);
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this.isDisabled = isDisabled;
        this.setPopupState(PopupState.Hidden);
    }
}
