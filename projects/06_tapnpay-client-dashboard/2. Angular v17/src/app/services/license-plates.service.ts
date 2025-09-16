import {Injectable, NgZone} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, of, throwError} from 'rxjs';
import {DebugService} from './debug.service';
import {
    LicensePlateCategoriesHttpResponse
} from "../_modals/modals-components/fleet-lpn-register/_interfaces/license-plate-categories-http-response";
import {SortedVehiclesList} from "../dashboard/profile/vehicles/vehicles.component";

export type LicensePlateType =
    | 'PERSONAL'
    | 'RENTAL';

export interface LicensePlateItem {
    id: string;
    lpn: string;
    lps: string;
    lpc: string;
    registered: string;
    end_date?: string;
    type?: LicensePlateType;
}

export interface AllLicensePlatesHttpResponse {
    plates: LicensePlateItem[],
    rental_plates: LicensePlateItem[]

}

export interface GetLicensePlatesResponseV2 {
    plates: LicensePlateItem[]
}

export interface PendingLPN {
    id: string;
    lpn: string;
    lps: string;
    lpc: string;
    rental: boolean;
    supported_types: string [];
}

export interface PendingLPNResponse {
    fee: number;
    plates: PendingLPN[];
    max_rental_date: Date;
    max_rental_days: number;
}

export interface PendingLPNsInvoiceResponse {
    status: 'OK' | 'ERROR';
    invoice_id: string;
    invoice_name: string;
    invoice_amount: number;
    invoice_items: string[];
}

export interface GetLicensePlateHistoryResponse {
    items: LicensePlateItem[];
}

@Injectable({
    providedIn: 'root'
})
export class LicensePlatesService {
    constructor(
        private http: HttpService,
        private zone: NgZone,
        private debugService: DebugService,
    ) {
        this.debugService.registerNewConsoleCommand('getLPNWithPBM', () => {
            return this.zone.run(() => {
                this.fetchLPNWithPBM().toPromise().catch(() => null).then((lpn) => {
                    console.warn(lpn);
                });
            });
        }, {help: `Fetch license plate with assigned PBM`});
    }

    getAllLicensePlates(): Observable<AllLicensePlatesHttpResponse> {
        return this.http.get('endpoint://license-plates.get')
            .pipe(
                take(1),
                catchError(error => {
                    console.warn('fetchLicensePlates error:', error);
                    return throwError(error);
                })
            );
    }

    unregLicensePlate(licensePlateId: string): Observable<number> {
        return this.http.delete('endpoint://license-plates.delete', {
            urlParams: {licensePlateId}
        }).pipe(
            take(1),
            map(response => response === 'OK' ? 0 : -1),
            catchError(error => {
                console.warn('deleteLicensePlate error:', error);
                return throwError(error.error.status_code);
            })
        );
    }

    addLicensePlate(newLicensePlate: { lp: string, rental: boolean }): Observable<number> {
        return this.http.post('endpoint://license-plates.add', {
            body: newLicensePlate
        }).pipe(
            take(1),
            map(response => response.status === 'OK' ? 0 : -1),
            catchError(error => {
                console.warn('addLicensePlate error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        );
    }

    fetchLPNWithPBM(): Observable<string> {
        return this.http.get('endpoint://license-plates.getWithPBM', {
            responseType: 'text'
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchLPNWithPBM error:', error);
                return throwError(error);
            })
        );
    }

    getPendingLPNs(): Observable<PendingLPNResponse> {
        return this.http.get('endpoint://license-plates.getPendingLPNs').pipe(
            take(1),
            catchError(error => {
                console.warn('fetchPendingLPNs error:', error);
                return throwError(error);
            })
        );
    }


    private handleError(error) {
        console.warn('getListOfLicensePlateTypes error:', error);
        return throwError(error);
    }

    public getListOfLicensePlatesCategories(data: {
        state: string,
        toll_authority_name: string
    }): Observable<LicensePlateCategoriesHttpResponse> {
        const URL = 'endpoint://license-plates.getLicensePlateCategories';

        return this.http.post(URL, {body: data})
            .pipe(catchError(this.handleError));
    }

    public checkPendingLPNs(pendingLPNIds: string[]): Observable<null | PendingLPNsInvoiceResponse> {
        return this.http.post('endpoint://license-plates.checkPendingLPNs',);
    }

    public acceptPendingLPNs(pendingLPNIds: string[]): Observable<null | PendingLPNsInvoiceResponse> {
        return this.http.post('endpoint://license-plates.acceptPendingLPNs', {
            body: {
                pending_license_plate_ids: pendingLPNIds
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK' ? response : null),
            catchError(error => {
                console.warn('acceptPendingLPNs error:', error);
                return throwError(error);
            })
        );

    }

    public acceptPendingLPNsWithRental(pendingLPNs: any[]): Observable<null | PendingLPNsInvoiceResponse> {
        return this.http.post('endpoint://license-plates.acceptPendingLPNs', {
            body: {
                pending_license_plates: pendingLPNs
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK' ? response : null),
            catchError(error => {
                console.warn('acceptPendingLPNs error:', error);
                return throwError(error);
            })
        );

    }

    public extendLPNRentalPeriod(LPN: LicensePlateItem, endDate) {
        const id = LPN.id;

        return this.http.post('endpoint://license-plates.extendRentalPeriod', {
            urlParams: {
                id: id
            },
            body: {
                end_date: endDate
            }
        });
    }

    public getLicensePlateCoverage(licensePlateId: string): Observable<any> {
        return this.http.get('endpoint://license-plates.getLicensePlateCoverage', {
            urlParams: {
                licensePlateId: licensePlateId
            }
        });
    }


    public getSupportedTaLPNTypes(): Observable<{ supported_types: string[]; }> {
        return this.http.get('endpoint://license-plates.getSupportedTaLPNTypes', {});
    }


    public getAllLicensePlatesV2(): Observable<GetLicensePlatesResponseV2> {
        return this.http.get('endpoint://license-plates.get-all', {});
    }


    public getAllLicensePlatesHistory(licensePlateId: string): Observable<GetLicensePlateHistoryResponse> {
        return this.http.get('endpoint://license-plates.getLicensePlateHistory', {
            urlParams: {
                licensePlateId: licensePlateId
            }
        });
    }

    public getCountOfActiveLPNs(): Observable<{ 'active': number }> {
        return this.http.get('endpoint://license-plates.get-active', {});
    }

    public sortLicensePlatesByRegistrationDate(licensePlates: LicensePlateItem[]): LicensePlateItem[] {
        return licensePlates.sort((a, b) => {
            if (a.registered > b.registered) {
                return -1;
            }
            if (a.registered < b.registered) {
                return 1;
            }
            return 0;
        });
    }

    public sortLicensePlateList(licensePlateList: LicensePlateItem[]): SortedVehiclesList {
        const vehiclesList: SortedVehiclesList = {
            active: {
                usual: [],
                rental: [],
            },
            deactivated: {
                usual: [],
                rental: [],
            },
        };

        licensePlateList.forEach((plate: LicensePlateItem) => {
            const type: LicensePlateType = plate.type;
            const isActive = !this.isLicensePlateExpired(plate);
            const category = isActive ? 'active' : 'deactivated';

            if (type === 'PERSONAL') {
                vehiclesList[category].usual.push(plate);
            } else if (type === 'RENTAL') {
                vehiclesList[category].rental.push(plate);
            }
        });

        return vehiclesList;
    }

    private isLicensePlateExpired(licensePlate: LicensePlateItem): boolean {
        return licensePlate.end_date && new Date(licensePlate.end_date) < new Date();
    }
}
