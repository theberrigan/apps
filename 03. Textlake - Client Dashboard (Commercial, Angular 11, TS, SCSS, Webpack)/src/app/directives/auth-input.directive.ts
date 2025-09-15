import {AfterViewInit, Directive, ElementRef, EventEmitter, OnDestroy, Output, Renderer2} from '@angular/core';
import {DeviceService} from '../services/device.service';

@Directive({
    selector: '[auth-input]'
})
export class AuthInputDirective implements AfterViewInit, OnDestroy {
    public isDestroyed : boolean = false;

    public isUserInteracted : boolean = false;

    constructor (
        private el : ElementRef,
        private renderer : Renderer2,
        private deviceService : DeviceService
    ) {}

    public ngAfterViewInit () : void {
        const labelEl = this.el.nativeElement;
        const inputEl = labelEl.querySelector('.auth__input');

        if (inputEl.value.trim()) {
            this.renderer.addClass(inputEl, 'auth__input_has-value');
        }

        this.renderer.listen(labelEl, 'click', () => inputEl.focus());

        const checkValue = () => {
            if (inputEl.value.trim().length) {
                this.renderer.addClass(inputEl, 'auth__input_has-value');
            } else {
                this.renderer.removeClass(inputEl, 'auth__input_has-value');
            }
        };

        this.renderer.listen(inputEl, 'focusin', () => {
            this.isUserInteracted = true;
        });

        this.renderer.listen(inputEl, 'focusout', () => checkValue());
        this.renderer.listen(inputEl, 'change', () => {
            this.isUserInteracted = true;
            checkValue();
        });

        // -----------

        const eyeEl = labelEl.querySelector('.auth__input-eye');

        if (eyeEl) {
            if (inputEl.type === 'text') {
                this.renderer.addClass(eyeEl, 'auth__input-eye_visible');
            }

            this.renderer.listen(eyeEl, 'click', (e : any) => {
                e.stopPropagation();

                if (inputEl.type === 'text') {
                    inputEl.type = 'password';
                    this.renderer.removeClass(eyeEl, 'auth__input-eye_visible');
                } else {
                    inputEl.type = 'text';
                    this.renderer.addClass(eyeEl, 'auth__input-eye_visible');
                }
            });
        }

        // -----------

        if (this.deviceService.browser.chrome) {
            const checkAutofill = (attempts : number) => {
                if (this.isUserInteracted || this.isDestroyed) {
                    return;
                }

                let hasAutofill : boolean = false;

                try {
                    hasAutofill = !!(inputEl.matches && inputEl.matches(':-webkit-autofill, :-internal-autofill-selected'));
                } catch (e) {}

                if (hasAutofill || !!inputEl.value) {
                    this.renderer.addClass(inputEl, 'auth__input_has-value');
                } else if (attempts) {
                    setTimeout(() => checkAutofill(attempts - 1), 100);
                }
            };

            checkAutofill(50);
        }

        this.renderer.addClass(labelEl, 'auth__control-label_ready');
    }

    public ngOnDestroy () : void {
        this.isDestroyed = true;
    }
}
