import {Injectable, NgZone} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {DebugService} from './debug.service';
import {StorageService} from './storage.service';
import {observableToBeFn} from 'rxjs/internal/testing/TestScheduler';

export interface LicensePlateItem {
    id : string;
    lpn : string;
    lps : string;
    lpc : string;
    registered : string;
}

export interface PendingLPN {
    id : string;
    lpn : string;
    lps : string;
    lpc : string;
}

export interface PendingLPNResponse {
    fee	: number;
    plates : PendingLPN[];
}

export interface PendingLPNsInvoiceResponse {
    status : 'OK' | 'ERROR';
    invoice_id : string;
    invoice_name : string;
    invoice_amount : number;
    invoice_items : string[];
}

@Injectable({
    providedIn: 'root'
})
export class LicensePlatesService {
    constructor (
        private http : HttpService,
        private zone : NgZone,
        private debugService : DebugService,
    ) {
        this.debugService.register('getLPNWithPBM', () => {
            return this.zone.run(() => {
                this.fetchLPNWithPBM().toPromise().catch(() => null).then((lpn) => {
                    console.warn(lpn);
                });
            });
        }, { help: `Fetch license plate with assigned PBM` });
    }

    fetchLicensePlates () : Observable<LicensePlateItem[]> {
        return this.http.get('endpoint://license-plates.get')
            .pipe(
                retry(1),
                take(1),
                map(({ plates }) => plates),
                catchError(error => {
                    console.warn('fetchLicensePlates error:', error);
                    return throwError(error);
                })
            );
    }

    unregLicensePlate (licensePlateId : string) : Observable<number> {
        return this.http.delete('endpoint://license-plates.delete', {
            urlParams: { licensePlateId }
        }).pipe(
            take(1),
            map(response => response === 'OK' ? 0 : -1),
            catchError(error => {
                console.warn('deleteLicensePlate error:', error);
                return throwError(error.error.status_code);
            })
        );
    }

    addLicensePlate (lp : string) : Observable<number> {
        return this.http.post('endpoint://license-plates.add', {
            body: { lp }
        }).pipe(
            take(1),
            map(response => response.status === 'OK' ? 0 : -1),
            catchError(error => {
                console.warn('addLicensePlate error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        );
    }

    fetchLPNWithPBM () : Observable<string> {
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

    fetchPendingLPNs () : Observable<PendingLPNResponse> {
        return this.http.get('endpoint://license-plates.getPendingLPNs').pipe(
            take(1),
            catchError(error => {
                console.warn('fetchPendingLPNs error:', error);
                return throwError(error);
            })
        );
    }

    acceptPendingLPNs (pendingLPNIds : string[]) : Observable<null | PendingLPNsInvoiceResponse> {
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
}
