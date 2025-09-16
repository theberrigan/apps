import {Component, Input, OnInit} from '@angular/core';

export interface CoverageMatrixHttpResponse {
    license_plates: CoverageMatrixLicensePlate[];
}

export interface CoverageMatrixLicensePlate {
    lps: string;
    lpn: string;
    coverage: CoverageMatrixTollAuthorityCoverage;
}

export interface CoverageMatrixTollAuthorityCoverage {
    string: matrixCoverageStatus;
}

export type matrixCoverageStatus =
    'ADD_PENDING'
    | 'ADDED'
    | 'REMOVED'
    | 'REMOVE_PENDING'
    | 'ADD_ERROR'
    | 'REMOVE_ERROR';

@Component({
    selector: 'app-coverage-matrix',
    templateUrl: './coverage-matrix.component.html',
    styleUrls: ['./coverage-matrix.component.scss']
})
export class CoverageMatrixComponent implements OnInit {

    @Input() data: CoverageMatrixLicensePlate[] = [];
    tollAuthoritiesNames: string[] = [];

    constructor() {
    }

    ngOnInit(): void {
        this.getTollAuthorities();
    }

    private getTollAuthorities(): void {
        const taCoverageMapByTaName: CoverageMatrixTollAuthorityCoverage = this.data[0]?.coverage || null;
        if (taCoverageMapByTaName) {
            this.tollAuthoritiesNames = Object.keys(taCoverageMapByTaName);
            return;
        }
    }


}
