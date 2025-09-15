import {Injectable, Renderer2} from '@angular/core';
import {ReplaySubject} from 'rxjs';

const attrsTrueValues = ['', 'true', 'yes', '1', true];

@Injectable({
    providedIn: 'root'
})
export class DomService {
    public readonly scrollbarSize: number;

    public onPageScrollToggle = new ReplaySubject<boolean>();

    public onDraggingToggle = new ReplaySubject<boolean>();

    private uniqueId: number = 0;

    private disableScrollIds: number[] = [];

    private disableSelectIds: number[] = [];

    private htmlClasses: { [className: string]: number[] } = {};

    constructor() {
        this.scrollbarSize = (() => {
            const box = document.createElement('div');
            box.style.cssText = 'position: fixed; left: -99999px; height: 100px; width: 100px; overflow: scroll;';
            document.body.appendChild(box);
            const scrollbarSize = box.offsetWidth - box.clientWidth;
            document.body.removeChild(box);
            return Math.max(scrollbarSize || 0, 0);
        })();
    }

    public parseBooleanAttr(value: any): boolean {
        return attrsTrueValues.includes(value);
    }

    public markEvent(e: Event, propKey: string, propValue: any = true): any {
        Object.defineProperty(e, `__${propKey}`, {value: propValue, configurable: true});
        return e;
    }

    public isHasEventMark(e: Event, propKey: string, propValue: any = true): boolean {
        return e[`__${propKey}`] === propValue;
    }

    public getEventMark(e: any, propKey: string): any {
        return e[`__${propKey}`];
    }

    public togglePageScroll(show: boolean): void {
        this.onPageScrollToggle.next(show);
    }

    public toggleDragging(isDragging: boolean): void {
        this.onDraggingToggle.next(isDragging);
    }

    public getParentBounding(el: HTMLElement, value: string): any {
        let parent: any = el;
        value = (value || '').toLowerCase();

        while ((parent = parent.parentElement || parent.parentNode)) {
            if (parent.dataset && parent.dataset.bound) {
                const match = (parent.dataset.bound || '').toLowerCase().split(/\s*,\s*/g);
                if (match.includes(value)) {
                    return parent;
                }
            }
        }

        return null;
    }

    disablePageScroll(): () => void {
        return this.pushHTMLClass('no-scroll');
    }

    disablePageSelect(): () => void {
        return this.pushHTMLClass('no-select');
    }

    pushHTMLClass(className: string): () => void {
        const id = this.getUniqueId();

        if (!this.htmlClasses[className]) {
            this.htmlClasses[className] = [];
        }

        this.htmlClasses[className].push(id);

        document.documentElement.classList.add(className);

        return () => {
            this.htmlClasses[className] = this.htmlClasses[className].filter(item => item !== id);

            if (!this.htmlClasses[className].length) {
                document.documentElement.classList.remove(className);
            }
        };
    }

    private getUniqueId(): number {
        return ++this.uniqueId;
    }
}
