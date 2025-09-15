import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {MapToolAuthorityNameStatesPipe} from "./map-tool-authority-name-states.pipe";


@NgModule({
    declarations: [MapToolAuthorityNameStatesPipe],
    imports: [
        CommonModule
    ],
    exports: [MapToolAuthorityNameStatesPipe]
})
export class MapToolAuthorityNamesStatesModule {
}
