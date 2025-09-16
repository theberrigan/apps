import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {DomService} from '../../../../services/dom.service';
import {UserService} from '../../../../services/user.service';
import {Router} from '@angular/router';
import {
    CarrierContractResponseData,
    ContractsService,
    PGContractItem,
    PGContractResponseData
} from '../../../../services/contracts.service';


type ListState = 'loading' | 'ready' | 'empty' | 'error';
type PreviewPopupState = 'loading' | 'ready' | 'error';


interface PGContract {
    id : number;
    name : string;
    charge : string;
    discount : string;
    startDate : string;
    endDate : string;
    status : string;
}

@Component({
    selector: 'pg-contract-list',
    templateUrl: './pg-contract-list.component.html',
    styleUrls: [ './pg-contract-list.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'pg-contract-list'
    },
})
export class PGContractListComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    listState : ListState = 'loading';

    canEdit : boolean = false;

    isPreviewPopupVisible : boolean = false;

    contracts : PGContractItem[];

    previewCache : { [ id : string ] : PGContractResponseData } = {};

    previewPopupState : PreviewPopupState = 'loading';

    contractToPreview : PGContractResponseData;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private domService : DomService,
        private userService : UserService,
        private contractsService : ContractsService,
    ) {
        this.titleService.setTitle('contracts.pg.list.page_title');
        this.listState = 'loading';
        this.canEdit = this.userService.checkPermission('CONTRACT_PAYMENT_GATEWAY_EDIT');
    }

    ngOnInit () {
        this.fetchContracts();
    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async fetchContracts () {
        this.contracts = await this.contractsService.fetchPGContracts().toPromise().catch(() => null);

        if (!this.contracts) {
            this.listState = 'error';
        } else if (this.contracts.length === 0) {
            this.listState = 'empty';
        } else {
            this.listState = 'ready';
        }
    }

    onActionsClick (e : MouseEvent) {
        this.domService.markEvent(e, 'contractActionsClick');
    }

    onContractClick (contractId : string, e : MouseEvent) {
        if (this.canEdit && !this.domService.hasEventMark(e, 'contractActionsClick')) {
            this.onEdit(contractId);
        }
    }

    onEdit (contractId : string) {
        if (!this.canEdit) {
            return;
        }

        this.router.navigate([ '/dashboard/contracts/payment-gateway', contractId ]);
        console.log('Edit', contractId);
    }

    async onPreview (contractId : string) {
        if (this.isPreviewPopupVisible) {
            return;
        }

        this.isPreviewPopupVisible = true;

        let contract : null | PGContractResponseData = this.previewCache[contractId] || null;

        if (contract) {
            this.previewPopupState = 'ready';
            this.contractToPreview = contract;
        } else {
            this.previewPopupState = 'loading';
            contract = await this.contractsService.fetchPGContract(contractId).toPromise().catch(() => null);

            if (contract) {
                this.previewCache[contractId] = contract;
                this.contractToPreview = contract;
                this.previewPopupState = 'ready';
            } else {
                this.contractToPreview = null;
                this.previewPopupState = 'error';
            }
        }

        console.log('Preview', this.contractToPreview);
    }

    onHidePreview () {
        this.isPreviewPopupVisible = false;
        this.contractToPreview = null;
    }
}
