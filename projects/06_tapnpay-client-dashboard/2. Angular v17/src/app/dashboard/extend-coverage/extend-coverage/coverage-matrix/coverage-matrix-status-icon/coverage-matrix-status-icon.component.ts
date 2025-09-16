import {Component, Input} from '@angular/core';
import {matrixCoverageStatus} from "../coverage-matrix.component";

@Component({
    selector: 'app-coverage-matrix-status-icon',
    templateUrl: './coverage-matrix-status-icon.component.html',
    styleUrls: ['./coverage-matrix-status-icon.component.scss']
})
export class CoverageMatrixStatusIconComponent {

    @Input() status: matrixCoverageStatus = 'ADD_ERROR';

    constructor() {
    }

}
