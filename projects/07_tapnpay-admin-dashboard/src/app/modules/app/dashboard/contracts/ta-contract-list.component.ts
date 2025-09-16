import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {
    ContractsService,
    TAContractItem,
    TAContractResponseData
} from '../../../../services/contracts.service';
import {DomService} from '../../../../services/dom.service';
import {UserService} from '../../../../services/user.service';
import {Router} from '@angular/router';
import {TAListItem, TAService} from '../../../../services/ta.service';


type ListState = 'loading' | 'ready' | 'empty' | 'error';
type PreviewPopupState = 'loading' | 'ready' | 'error';




@Component({
    selector: 'ta-contract-list',
    templateUrl: './ta-contract-list.component.html',
    styleUrls: [ './ta-contract-list.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'ta-contract-list'
    },
})
export class TAContractListComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    listState : ListState = 'loading';

    canEdit : boolean = false;

    isPreviewPopupVisible : boolean = false;

    contracts : TAContractItem[];

    previewCache : { [ id : string ] : TAContractResponseData } = {};

    previewPopupState : PreviewPopupState = 'loading';

    contractToPreview : TAContractResponseData;

    taMap : { [ id : string ] : string } = {};

    constructor (
        private router : Router,
        private titleService : TitleService,
        private domService : DomService,
        private userService : UserService,
        private contractsService : ContractsService,
        private taService : TAService,
    ) {
        this.titleService.setTitle('contracts.ta.list.page_title');
        this.listState = 'loading';
        this.canEdit = this.userService.checkPermission('CONTRACT_TOLL_AUTHORITY_EDIT');
    }

    ngOnInit () {
        this.fetchData();
    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async fetchData () {
        const responses : null | [ TAContractItem[], TAListItem[] ] = await Promise.all([
            this.contractsService.fetchTAContracts().toPromise(),
            this.taService.fetchTAs().toPromise(),
        ]).catch(() => null);

        console.log(responses);

        if (!responses) {
            this.listState = 'error';
            return;
        }

        this.contracts = responses[0];
        this.taMap = responses[1].reduce((acc, item) => {
            acc[item.id] = item.display_name;
            return acc;
        }, {});

        if (this.contracts.length === 0) {
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

        this.router.navigate([ '/dashboard/contracts/toll-authority', contractId ]);
        console.log('Edit', contractId);
    }

    async onPreview (contractId : string) {
        if (this.isPreviewPopupVisible) {
            return;
        }

        this.isPreviewPopupVisible = true;

        let contract : null | TAContractResponseData = this.previewCache[contractId] || null;

        if (contract) {
            this.previewPopupState = 'ready';
            this.contractToPreview = contract;
        } else {
            this.previewPopupState = 'loading';
            contract = await this.contractsService.fetchTAContract(contractId).toPromise().catch(() => null);

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
