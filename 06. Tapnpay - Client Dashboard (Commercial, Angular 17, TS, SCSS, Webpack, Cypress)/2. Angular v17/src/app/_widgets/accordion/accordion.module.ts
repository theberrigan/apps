import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AccordionContent} from './directives/accordion-content.directive';
import {AccordionHeader} from './directives/accordion-header.directive';
import {AccordionItem} from './directives/accordion-item.directive';
import {AccordionTitle} from './directives/accordion-title.directive';
import {AccordionComponent} from './accordion/accordion.component';


@NgModule({
    declarations: [AccordionContent, AccordionHeader, AccordionItem, AccordionTitle, AccordionComponent],
    imports: [
        CommonModule
    ],
    exports: [AccordionContent, AccordionHeader, AccordionItem, AccordionTitle, AccordionComponent]
})
export class AccordionModule {
}
