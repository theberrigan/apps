import {Directive, ElementRef, HostBinding, Input, OnChanges, OnInit, SimpleChanges} from '@angular/core';
import {animate, AnimationBuilder, AnimationPlayer, keyframes, style} from '@angular/animations';

@Directive({
    selector: '[appCollapseAnimated]'
})
export class CollapseAnimatedDirective implements OnChanges, OnInit {
    private static readonly SHOW_STYLE = 'show';
    private static readonly COLLAPSING = 'collapsing';

    @Input('appCollapseAnimated')
    collapsed = true;

    @Input()
    skipClosingAnimation = false;

    @Input()
    listItems: number = 2;

    @HostBinding('class.collapse')
    private readonly addCollapseClass = true;

    private currentEffect: AnimationPlayer;
    private _closeEffect: AnimationPlayer;
    private _openEffect: AnimationPlayer;

    constructor(private el: ElementRef,
                private builder: AnimationBuilder) {

    }

    ngOnInit(): void {
        if (!this.collapsed) {
            this.getClassList().add(CollapseAnimatedDirective.SHOW_STYLE);
        }
    }

    private get openEffect(): AnimationPlayer {
        if (!this._openEffect) {
            this._openEffect = this.builder.build(animate('500ms', keyframes([
                style({height: '63px'}),
                style({height: this.getMaxHeight() + 'px'}),
            ]))).create(this.el.nativeElement);
        }
        this._openEffect.onDone(() => this.effectDone());
        return this._openEffect;
    }


    private get closeEffect(): AnimationPlayer {
        if (!this._closeEffect) {
            this._closeEffect = this.builder.build(animate('500ms', keyframes([
                style({height: '*'}),
                style({height: '63px'}),
            ]))).create(this.el.nativeElement);
        }
        this._closeEffect.onDone(() => this.effectDone());
        return this._closeEffect;
    }

    private effectDone() {
        if (this.collapsed) {
            this.getClassList().remove(CollapseAnimatedDirective.SHOW_STYLE);
        }
        this.getClassList().remove(CollapseAnimatedDirective.COLLAPSING);
        if (this.currentEffect) {
            this.currentEffect.reset();
            this.currentEffect = null;
        }
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes.collapsed && !changes.collapsed.firstChange) {
            if (changes.collapsed.previousValue === true && changes.collapsed.currentValue === false) {
                this.startOpening();
            }
            if (changes.collapsed.previousValue === false && changes.collapsed.currentValue === true) {
                this.startClosing();
            }
        }
    }

    private startOpening(): void {
        this.getClassList().add(CollapseAnimatedDirective.SHOW_STYLE);
        const effect = this.openEffect;
        this.playEffect(effect);
    }

    private getClassList() {
        const nativeElement = this.el.nativeElement as HTMLElement;
        return nativeElement.classList;
    }

    private startClosing(): void {
        const effect = this.closeEffect;
        if (this.skipClosingAnimation) {
            this.effectDone();
        } else {
            this.playEffect(effect);
        }
    }

    private playEffect(effect: AnimationPlayer) {
        if (!this.currentEffect) {
            this.getClassList().add(CollapseAnimatedDirective.COLLAPSING);
            this.currentEffect = effect;
            this.currentEffect.play();
        }
    }

    private getMaxHeight(): number {
        return (this.listItems * 32) + 80;
    }
}
