import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ExtendCoverageComponent} from './extend-coverage/extend-coverage.component';
import {RouterModule, Routes} from "@angular/router";
import {
    ExtendCoverageSelectorComponent
} from './extend-coverage/extend-coverage-selector/extend-coverage-selector.component';
import {SharedModule} from "../../_shared/shared.module";
import {PagePanelModule} from "../page-panel/page-panel.module";
import {PopupModule} from "../../_widgets/popup/popup.module";
import {TermsInnerModule} from "../../_shared/terms-inner/terms-inner.module";
import {
    ExtendCoverageNotificationMessageComponent
} from './extend-coverage/extend-coverage-notification-message/extend-coverage-notification-message.component';
import {
    ActiveTollAuthoritiesListComponent
} from './extend-coverage/active-toll-authorities-list/active-toll-authorities-list.component';
import {AppBarModule} from "../../app-bar/app-bar.module";
import {
    MapToolAuthorityNamesStatesModule
} from "./map-tool-authority-names-states/map-tool-authority-names-states.module";
import {CoverageMatrixComponent} from './extend-coverage/coverage-matrix/coverage-matrix.component';
import {
    CoverageMatrixStatusIconComponent
} from './extend-coverage/coverage-matrix/coverage-matrix-status-icon/coverage-matrix-status-icon.component';
import {
    MatrixStatusesIconsInfoComponent
} from './extend-coverage/coverage-matrix/matrix-statuses-icons-info/matrix-statuses-icons-info.component';
import {ButtonModule} from "../../_widgets/button/button.module";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {TaNameToShowPipe} from './extend-coverage/ta-name-to-show.pipe';

const routes: Routes = [
    {
        path: '',
        component: ExtendCoverageComponent,
    }
];

@NgModule({
    declarations: [ExtendCoverageComponent, ExtendCoverageSelectorComponent, ExtendCoverageNotificationMessageComponent, ActiveTollAuthoritiesListComponent, CoverageMatrixComponent, CoverageMatrixStatusIconComponent, MatrixStatusesIconsInfoComponent, TaNameToShowPipe],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        SharedModule,
        PagePanelModule,
        PopupModule,
        TermsInnerModule,
        AppBarModule,
        MapToolAuthorityNamesStatesModule,
        ButtonModule,
        LoaderModule,
    ]
})
export class ExtendCoverageModule {
}
