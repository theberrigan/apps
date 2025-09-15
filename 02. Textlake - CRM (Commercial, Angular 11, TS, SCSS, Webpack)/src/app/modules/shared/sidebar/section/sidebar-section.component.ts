import {AfterContentInit, Component, ContentChild, ViewEncapsulation} from '@angular/core';
import {SidebarLabelComponent} from '../label/sidebar-label.component';

@Component({
    selector: '.sidebar__section',
    exportAs: 'sidebarSection',
    templateUrl: './sidebar-section.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        '[class.sidebar__section_has-label]': 'label',
        '[class.sidebar__section_can-collapse]': 'label && label.canCollapse',
        '[class.sidebar__section_collapsed]': 'label && label.isCollapsed'
    }
})
export class SidebarSectionComponent { // implements AfterContentInit {
    @ContentChild(SidebarLabelComponent)
    public label : SidebarLabelComponent;

    // public isCollapsed : boolean = false;
    //
    // public ngAfterContentInit () : void {
    //     if (!this.label) {
    //         return;
    //     }
    //
    //     this.isCollapsed = this.label.isCollapsed;
    //
    //     this.label.onCollapse.subscribe((isCollapsed) => {
    //         this.isCollapsed = isCollapsed;
    //         console.log('isCollapsed', this.isCollapsed);
    //     });
    // }
}
