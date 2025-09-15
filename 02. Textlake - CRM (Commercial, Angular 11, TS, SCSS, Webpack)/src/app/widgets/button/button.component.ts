import {
    AfterContentInit,
    Component, ElementRef,
    HostListener,
    Input, OnInit, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {includes} from 'lodash';

@Component({
    selector: '.button',
    exportAs: 'button',
    templateUrl: './button.component.html',
    encapsulation: ViewEncapsulation.None
})
export class ButtonComponent implements OnInit, AfterContentInit {
    @Input()
    public set isAffectedByFieldset (isAffectedByFieldset : boolean) {
        const el = this.el.nativeElement;

        if (isAffectedByFieldset) {
            this.isLink && console.log(`button: '_affected-by-fieldset' only makes sense if button created with tag <a>.`);
            this.renderer.addClass(el, 'button_affected-by-fieldset');
        } else {
            this.renderer.removeClass(el, 'button_affected-by-fieldset');
        }
    }

    public get isAffectedByFieldset () : boolean {
        return this.el.nativeElement.classList.contains('button_affected-by-fieldset');
    }

    @Input()
    public set isProgress (isProgress : boolean) {
        const el = this.el.nativeElement;

        if (isProgress) {
            this.renderer.addClass(el, 'button_has-progress');
        } else {
            this.renderer.removeClass(el, 'button_has-progress');
        }
    }

    public get isProgress () : boolean {
        return this.el.nativeElement.classList.contains('button_has-progress');
    }

    @Input()
    public set isDisabled (isDisabled : boolean) {
        const el = this.el.nativeElement;

        if (isDisabled) {
            this.isButton && (el.disabled = true);
            this.renderer.addClass(el, 'button_disabled');
        } else {
            this.isButton && (el.disabled = false);
            this.renderer.removeClass(el, 'button_disabled');
        }
    }

    public get isDisabled () : boolean {
        const el = this.el.nativeElement;

        return (
            this.isButton && el.disabled ||   // button disabled by property
            el.classList.contains('button_disabled') ||  // button or link disabled by class name
            el.closest('fieldset[disabled]') && (this.isButton || this.isLink && el.classList.contains('button_affected-by-fieldset'))  // button or link-affected-by-fieldset disabled by fieldset
        );
    }

    public isButton : boolean;

    public isLink : boolean;

    constructor (
        public el : ElementRef,
        public renderer : Renderer2
    ) {}

    @HostListener('click', [ '$event' ])
    public onClick (e : any) : void {
        if (this.isDisabled) {
            e.preventDefault();
            return;
        }
    }

    public ngOnInit () : void {
        const el = this.el.nativeElement;
        const tag = el.tagName.toUpperCase();

        this.isButton = includes([ 'BUTTON', 'INPUT' ], tag);
        this.isLink = tag === 'A';

        if (this.isButton && !el.getAttribute('type')) {
            el.type = 'button';
        }
    }

    public ngAfterContentInit () : void {

    }
}
