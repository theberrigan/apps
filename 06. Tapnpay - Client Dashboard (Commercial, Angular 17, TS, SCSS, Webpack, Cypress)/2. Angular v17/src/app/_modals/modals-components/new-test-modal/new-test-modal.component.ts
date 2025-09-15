import {
    AfterViewInit,
    Component,
    ComponentFactoryResolver,
    EventEmitter,
    Injector,
    Input, OnInit, Output,
    ViewChild,
    ViewContainerRef
} from '@angular/core';

type modalTypes = 'alert' | 'confirm' | 'choose' | 'form' | 'custom';

@Component({
    selector: 'app-new-test-modal',
    templateUrl: './new-test-modal.component.html',
    styleUrls: ['./new-test-modal.component.css']
})
export class NewTestModalComponent implements OnInit, AfterViewInit {
    public data: any;
    public outputEvent: EventEmitter<{ action: string, data: any }> = new EventEmitter();
    @ViewChild('dynamicContent', {read: ViewContainerRef}) dynamicContentContainer: ViewContainerRef;
    @Input() renderedComponent: any;
    @Input() componentData: any;
    @Output() cancelAction = new EventEmitter();
    @Output() submitAction = new EventEmitter();
    isOkButtonProgress: boolean = false;
    modalConfig: any = {
        titleTranslateKey: '',
        modalType: 'alert' as modalTypes,
        okButtonTranslateKey: '',
        cancelButtonTranslateKey: '',
    }

    constructor(private resolver: ComponentFactoryResolver, private injector: Injector) {
    }

    ngOnInit() {
    }

    ngAfterViewInit() {
        if (this.renderedComponent) {
            const componentRef = this.createDynamicComponent(this.renderedComponent, this.componentData);
            this.attachComponent(componentRef, this.dynamicContentContainer);
        }
    }


    public close(): void {
        this.outputEvent.emit(
            {
                action: 'close',
                data: null
            }
        );
    }

    open(compone) {

    }

    private createDynamicComponent(component, data) {
        const factory = this.resolver.resolveComponentFactory(component);
        const componentRef = factory.create(this.injector);
        if (data && componentRef.instance.hasOwnProperty('data')) {
            componentRef.instance['data'] = data;
        }
        return componentRef;
    }

    private attachComponent<T>(componentRef: any, containerRef: ViewContainerRef) {
        containerRef.insert(componentRef.hostView);
    }

    cancel() {
        this.close();
    }

    submit() {
        this.submitAction.emit();
    }
}
