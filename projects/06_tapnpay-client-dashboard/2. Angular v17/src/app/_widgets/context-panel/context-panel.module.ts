import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ContextPanelComponent} from "./context-panel/context-panel.component";


@NgModule({
    declarations: [ContextPanelComponent],
    imports: [
        CommonModule
    ],
    exports: [ContextPanelComponent]
})
export class ContextPanelModule {
}
