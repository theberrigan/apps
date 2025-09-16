import {
    ChangeDetectionStrategy,
    Component, ElementRef, HostListener,
    OnDestroy,
    OnInit, Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
// import * as hpccWasm from "@hpcc-js/wasm";
import { graphviz }  from 'd3-graphviz';
import {TitleService} from '../../../../services/title.service';
import {ToastService} from '../../../../services/toast.service';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {TACategory, TAPropData, TAService} from '../../../../services/ta.service';
import {LangService} from '../../../../services/lang.service';
import {DomService} from '../../../../services/dom.service';
import {animate, style, transition, trigger} from '@angular/animations';
import {GraphService} from '../../../../services/graph.service';
import {defer} from '../../../../lib/utils';

type State = 'loading' | 'ready' | 'empty' | 'error';

@Component({
    selector: 'ta-editor',
    templateUrl: './ta-editor.component.html',
    styleUrls: [ './ta-editor.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'ta-editor'
    },
    animations: [
        trigger('tooltipPopup', [
            transition(':enter', [
                style({ transform: 'translateY(-10px)', opacity: 0 }),
                animate('0.1s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: '*', opacity: '*' }))
            ]),
            transition(':leave', [
                style({ transform: '*', opacity: '*' }),
                animate('0.1s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'translateY(-10px)', opacity: 0 }))
            ])
        ]),
    ],
})
export class TAEditorComponent implements OnInit, OnDestroy, CanDeactivate<boolean> {
    subs : Subscription[] = [];

    state : State = 'loading';

    categories : TACategory[];

    taId : number;

    isSubmitting : boolean = false;

    hasChanges : boolean = false;

    activeTooltipName : string;

    isRegFlowGraphLoading : boolean = false;

    isRegFlowGraphVisible : boolean = false;

    regFlowGraphs : { [ key : string ] : string } = {};

    @ViewChild('regFlowGraphEl')
    regFlowGraphEl : ElementRef;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private langService : LangService,
        private titleService : TitleService,
        private domService : DomService,
        private taService : TAService,
        private graphService : GraphService,
        private toastService : ToastService,
    ) {
        this.titleService.setTitle('ta.editor.page_title');
        this.state = 'loading';
    }

    async ngOnInit () {
        this.taId = this.route.snapshot.params['id'] || null;

        if (!this.taId) {
            this.state = 'error';
            return;
        }

        const categories = await this.taService.fetchTAProps(this.taId).toPromise().catch(() => null);

        if (categories) {
            this.categories = this.preprocessCategories(categories);
            this.state = this.categories.length ? 'ready' : 'empty';
        } else {
            this.state = 'error';
        }
    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onChange () {
        this.hasChanges = true;
    }

    async onSave () {
        if (this.isSubmitting || !this.hasChanges) {
            return;
        }

        this.isSubmitting = true;

        const props : TAPropData[] = [];

        this.categories.forEach(cat => {
            cat.properties.forEach(prop => {
                props.push({
                    name: prop.name,
                    value: prop.value
                });
            });
        });

        const categories = await this.taService.updateTAProps(this.taId, props).toPromise().catch(() => null);

        this.isSubmitting = false;

        if (categories) {
            this.categories = this.preprocessCategories(categories);
            this.hasChanges = false;
            this.state = this.categories.length ? 'ready' : 'empty';
            this.toastService.create({
                message: [ 'ta.editor.save_success' ],
                timeout: 3500
            });
        } else {
            this.state = 'error';
            this.toastService.create({
                message: [ 'ta.editor.save_error' ],
                timeout: 7000
            });
        }
    }

    preprocessCategories (categories : null | TACategory[]) {
        if (!categories) {
            return null;
        }

        // Don't show description if it matches the display name
        categories.forEach(cat => {
            cat.properties.forEach(prop => {
                if (!prop.description || prop.description === prop.display_name) {
                    prop.description = null;
                }
            });
        });

        return categories;
    }

    onBack () {
        this.router.navigateByUrl('/dashboard/toll-authorities');
    }

    canDeactivate () : boolean {
        if (this.hasChanges) {
            const message = this.langService.translate('ta.editor.confirm_discard');
            return window.confirm(message);
        }

        return true;
    }

    onTooltipTriggerClick (e : MouseEvent, propName : string) {
        this.domService.markEvent(e, 'taPTTClick');
        this.activeTooltipName = this.activeTooltipName === propName ? null : propName;
    }

    onTooltipPopupClick (e : MouseEvent) {
        this.domService.markEvent(e, 'taPTPClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : MouseEvent) {
        if (!this.domService.hasEventMark(e, 'taPTTClick') && !this.domService.hasEventMark(e, 'taPTPClick')) {
            this.activeTooltipName = null;
        }
    }

    async onLoadRegFlowGraph (nodeId : string) {
        nodeId = (nodeId || '').trim();

        if (!nodeId) {
            return;
        }

        if (!this.regFlowGraphs[nodeId]) {
            this.isRegFlowGraphLoading = true;
            this.regFlowGraphs[nodeId] = await this.graphService.fetchGraph(nodeId).toPromise().catch(() => null);
            this.isRegFlowGraphLoading = false;
        }

        if (this.regFlowGraphs[nodeId]) {
            this.showRegFlowGraph(this.regFlowGraphs[nodeId]);
        }
    }

    showRegFlowGraph (graph : string) {
        this.onGraphShow();

        defer(() => {
            const contEl = this.regFlowGraphEl.nativeElement;
            const contRect = contEl.getBoundingClientRect();

            graphviz(this.regFlowGraphEl.nativeElement, {
                width: contRect.width,
                height: contRect.height,
                fit: true
            }).renderDot(graph);
        });
    }

    onGraphShow () {
        this.isRegFlowGraphVisible = true;
        this.renderer.addClass(document.body, 'graph-popup-active');
    }

    onGraphClose () {
        this.isRegFlowGraphVisible = false;
        this.renderer.removeClass(document.body, 'graph-popup-active');
    }

    canShowRegFlowGraph (value : string) : boolean {
        return !this.isRegFlowGraphLoading && value.trim().length > 0;
    }
}
