// modal.service.ts
import {
    Injectable,
    ComponentFactoryResolver,
    ApplicationRef,
    Injector,
    EmbeddedViewRef,
    ComponentRef
} from '@angular/core';
import {NewTestModalComponent} from "../modals-components/new-test-modal/new-test-modal.component";

@Injectable({
    providedIn: 'root',
})
export class ModalService {
    private modalComponentRef: ComponentRef<any>;

    constructor(private componentFactoryResolver: ComponentFactoryResolver, private appRef: ApplicationRef, private injector: Injector) {
    }

    open(component: any, data: any): ComponentRef<NewTestModalComponent> {

        const componentRef: ComponentRef<any> = this.componentFactoryResolver.resolveComponentFactory(NewTestModalComponent).create(this.injector);

        this.appRef.attachView(componentRef.hostView);

        const domElem = (componentRef.hostView as EmbeddedViewRef<any>).rootNodes[0] as HTMLElement;

        document.body.appendChild(domElem);


        if (data) {
            componentRef.instance.data = data;
            componentRef.instance.renderedComponent = component;
        }

        this.modalComponentRef = componentRef;
        return componentRef;
    }

    public close(): void {
        this.appRef.detachView(this.modalComponentRef.hostView);
        this.modalComponentRef.destroy();
    }
}



