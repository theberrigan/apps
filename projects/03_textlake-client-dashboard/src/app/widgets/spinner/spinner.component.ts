import {Component, ElementRef, Renderer2, ViewEncapsulation} from '@angular/core';

@Component({
    selector: 'spinner',
    exportAs: 'spinner',
    templateUrl: './spinner.component.html',
    encapsulation: ViewEncapsulation.None
})
export class SpinnerComponent {
    constructor (
        public el : ElementRef,
        public renderer : Renderer2
    ) {
        if (!el.nativeElement.classList.contains('spinner')) {
            this.renderer.addClass(el.nativeElement, 'spinner');
        }
    }
}
