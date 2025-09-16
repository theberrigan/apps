import {Injectable} from '@angular/core';
import {HttpService} from "../../services/http.service";
import {Observable} from "rxjs";
import {CoverageMatrixHttpResponse} from "./extend-coverage/coverage-matrix/coverage-matrix.component";


export interface ExtendCoverageHttpResponse {
    coverage: TollAuthorityItem[];
}

export interface TollAuthorityItem {
    toll_authority_name: string;
    terms_name: string;
}

@Injectable({
    providedIn: 'root'
})
export class ExtendCoverageService {

    constructor(private http: HttpService) {
    }


    getActiveCoverage(): Observable<ExtendCoverageHttpResponse> {
        return this.http.get('endpoint://extend-coverage.enrolled');
    }

    getListOfExtendableCoverages(): Observable<ExtendCoverageHttpResponse> {
        return this.http.get('endpoint://extend-coverage.extended');
    }

    extendCoverage(listOfNames: string[]) {
        return this.http.post('endpoint://extend-coverage.extend', {
            body: {
                toll_authorities: listOfNames
            }
        });
    }

    getExtendCoverageMapping(): Observable<CoverageMatrixHttpResponse> {
        return this.http.get('endpoint://extend-coverage.mapping');
    }
}
