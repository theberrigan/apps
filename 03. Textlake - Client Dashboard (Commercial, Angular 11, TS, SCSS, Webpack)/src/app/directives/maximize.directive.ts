import { Directive, ElementRef, Renderer2 } from '@angular/core';

@Directive({
    selector: '[maximize]'
})
export class MaximizeDirective {
    constructor (
        public el : ElementRef,
        public renderer : Renderer2
    ) {
        this.redraw();
        this.renderer.listen(window, 'resize', () => this.redraw());
    }

    public redraw () : void {
        this.el && this.renderer.setStyle(this.el.nativeElement, 'min-height', window.innerHeight + 'px');
    }
}