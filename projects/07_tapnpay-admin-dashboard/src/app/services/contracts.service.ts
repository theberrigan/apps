import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';


export interface CarrierContractItem {
    id : string;
    name : string;
    integrator : string;
    rate : number;
    enabled : boolean;
    volume_discount : boolean;
    start_date : string;
    end_date : string;
}

export interface ContractTier {
    volume : number;
    rate : number;
    fee : number;
    minimum : number;
}

export interface ContractContact {
    name : string;
    phone : string;
    email : string;
}

export interface CarrierContractRequestData {
    integrator : string;
    name : string;
    carrier_group : string;
    start_date : string;
    end_date : string;
    enabled : boolean;
    document_id : string;
    tier1 : ContractTier;
    tier2 : ContractTier;
    tier3 : ContractTier;
}

export interface CarrierContractResponseData {
    id : string;
    integrator : string;
    integrators : string[];
    name : string;
    carrier_group : string;
    carrier_groups : string[];
    start_date : string;
    end_date : string;
    enabled	: boolean;
    document_id : string;
    document_name : string;
    tier1 : ContractTier;
    tier2 : ContractTier;
    tier3 : ContractTier;
}

export interface PGContractItem {
    id : string;
    name : string;
    rate : number;
    enabled : boolean;
    volume_discount : boolean;
    start_date : string;
    end_date : string;
}

export interface PGContractRequestData {
    gateway : string;
    name : string;
    start_date : string;
    end_date : string;
    enabled : boolean;
    document_id : string;
    tier1 : ContractTier;
    tier2 : ContractTier;
    tier3 : ContractTier;
}

export interface PGContractResponseData {
    id : string;
    gateway : string;
    gateways : string[];
    name : string;
    start_date : string;
    end_date : string;
    enabled	: boolean;
    document_id : string;
    document_name : string;
    tier1 : ContractTier;
    tier2 : ContractTier;
    tier3 : ContractTier;
}

export interface TAContractItem {
    id : string;
    name : string;
    start_date : string;
    end_date : string;
    status : string;
}

export interface TAContractRequestData {
    name : string;
    enabled : boolean;
    toll_authority_id : string;
    start_date : string;
    end_date : string;
    ap_carrying_days : number;
    saas_fee_structure : string;
    saas_fee_amount : number;
    document_id : string;
    customer_contact : ContractContact;
    paypal_contact : ContractContact;
    tnp_contact : ContractContact;
    dcb_tier1 : ContractTier;
    dcb_tier2 : ContractTier;
    dcb_tier3 : ContractTier;
    credit_card_tier1 : ContractTier;
    credit_card_tier2 : ContractTier;
    credit_card_tier3 : ContractTier;
    debit_card_tier1 : ContractTier;
    debit_card_tier2 : ContractTier;
    debit_card_tier3 : ContractTier;
    wallet_tier1 : ContractTier;
    wallet_tier2 : ContractTier;
    wallet_tier3 : ContractTier;
    paypal_tier1 : ContractTier;
    paypal_tier2 : ContractTier;
    paypal_tier3 : ContractTier;
}

export interface TAContractResponseData {
    id : string;
    name : string;
    enabled : boolean;
    toll_authority_id : number;
    start_date : string;
    end_date : string;
    ap_carrying_days : number;
    saas_fee_structure : string;
    saas_fee_amount : number;
    document_id : string;
    document_name : string;
    customer_contact : ContractContact;
    paypal_contact : ContractContact;
    tnp_contact : ContractContact;
    dcb_tier1 : ContractTier;
    dcb_tier2 : ContractTier;
    dcb_tier3 : ContractTier;
    credit_card_tier1 : ContractTier;
    credit_card_tier2 : ContractTier;
    credit_card_tier3 : ContractTier;
    debit_card_tier1 : ContractTier;
    debit_card_tier2 : ContractTier;
    debit_card_tier3 : ContractTier;
    wallet_tier1 : ContractTier;
    wallet_tier2 : ContractTier;
    wallet_tier3 : ContractTier;
    paypal_tier1 : ContractTier;
    paypal_tier2 : ContractTier;
    paypal_tier3 : ContractTier;
}


@Injectable({
    providedIn: 'root'
})
export class ContractsService {
    loader : Promise<any> = null;

    constructor (
        private http : HttpService
    ) {}

    fetchCarrierContracts () : Observable<CarrierContractItem[]> {
        return this.http.get('endpoint://contracts.getAllCarrier').pipe(
            take(1),
            map(response => response.items || []),
            catchError(error => {
                console.warn('fetchCarrierContracts error:', error);
                return throwError(error);
            })
        );
    }

    createCarrierContract (data : CarrierContractRequestData) : Observable<CarrierContractResponseData> {
        return this.http.post('endpoint://contracts.createCarrier', {
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createCarrierContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchCarrierContract (contractId : string) : Observable<CarrierContractResponseData> {
        return this.http.get('endpoint://contracts.getCarrier', {
            urlParams: { contractId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchCarrierContract error:', error);
                return throwError(error);
            })
        );
    }

    updateCarrierContract (contractId : string, data : CarrierContractRequestData) : Observable<CarrierContractResponseData> {
        return this.http.put('endpoint://contracts.updateCarrier', {
            urlParams: { contractId },
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('updateCarrierContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchIntegrators () : Observable<string[]> {
        return this.http.get('endpoint://contracts.getIntegrators').pipe(
            take(1),
            map(response => response || []),
            catchError(error => {
                console.warn('fetchIntegrators error:', error);
                return throwError(error);
            })
        );
    }

    fetchCarrierGroups () : Observable<string[]> {
        return this.http.get('endpoint://contracts.getCarrierGroups').pipe(
            take(1),
            map(response => response || []),
            catchError(error => {
                console.warn('fetchCarrierGroups error:', error);
                return throwError(error);
            })
        );
    }

    // -----------------------------------------------------------------------------------------------------------------

    fetchPGContracts () : Observable<PGContractItem[]> {
        return this.http.get('endpoint://contracts.getAllPG').pipe(
            take(1),
            map(response => response.items || []),
            catchError(error => {
                console.warn('fetchPGContracts error:', error);
                return throwError(error);
            })
        );
    }

    createPGContract (data : PGContractRequestData) : Observable<PGContractResponseData> {
        return this.http.post('endpoint://contracts.createPG', {
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createPGContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchPGContract (contractId : string) : Observable<PGContractResponseData> {
        return this.http.get('endpoint://contracts.getPG', {
            urlParams: { contractId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchPGContract error:', error);
                return throwError(error);
            })
        );
    }

    updatePGContract (contractId : string, data : PGContractRequestData) : Observable<PGContractResponseData> {
        return this.http.put('endpoint://contracts.updatePG', {
            urlParams: { contractId },
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('updatePGContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchGateways () : Observable<string[]> {
        return this.http.get('endpoint://contracts.getGateways').pipe(
            take(1),
            map(response => response || []),
            catchError(error => {
                console.warn('fetchGateways error:', error);
                return throwError(error);
            })
        );
    }

    // -----------------------------------------------------------------------------------------------------------------

    fetchTAContracts () : Observable<TAContractItem[]> {
        return this.http.get('endpoint://contracts.getAllTA').pipe(
            take(1),
            map(response => response.items || []),
            catchError(error => {
                console.warn('fetchTAContracts error:', error);
                return throwError(error);
            })
        );
    }

    createTAContract (data : TAContractRequestData) : Observable<TAContractResponseData> {
        return this.http.post('endpoint://contracts.createTA', {
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createTAContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchTAContract (contractId : string) : Observable<TAContractResponseData> {
        return this.http.get('endpoint://contracts.getTA', {
            urlParams: { contractId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchTAContract error:', error);
                return throwError(error);
            })
        );
    }

    updateTAContract (contractId : string, data : TAContractRequestData) : Observable<TAContractResponseData> {
        return this.http.put('endpoint://contracts.updateTA', {
            urlParams: { contractId },
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('updateTAContract error:', error);
                return throwError(error);
            })
        );
    }

    fetchSaasFeeStructures () : Observable<string[]> {
        return this.http.get('endpoint://contracts.getSaasFee').pipe(
            take(1),
            map(response => response || []),
            catchError(error => {
                console.warn('fetchSaasFeeStructures error:', error);
                return throwError(error);
            })
        );
    }
}
