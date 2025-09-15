import {
    ChangeDetectionStrategy,
    Component, ElementRef,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {ActivatedRoute, Router} from '@angular/router';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Location} from '@angular/common';
import {ToastService} from '../../../../services/toast.service';
import {
    ContractsService, PGContractRequestData, PGContractResponseData
} from '../../../../services/contracts.service';
import {divFloat, mulFloat} from '../../../../lib/utils';
import {DocumentsService} from '../../../../services/documents.service';


type State = 'loading' | 'ready' | 'error';

interface SelectOption {
    value : null | string;
    display : string;
}

interface CurrentDoc {
    id : string;
    name : string;
    downloadUrl : string;
}

interface UploadDoc {
    id : string;
    isUploaded : boolean;
    file : File;
}


@Component({
    selector: 'pg-contract',
    templateUrl: './pg-contract.component.html',
    styleUrls: [ './pg-contract.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'pg-contract'
    },
})
export class PGContractComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    state : State = 'loading';

    isSubmitting : boolean = false;

    gatewayOptions : SelectOption[];

    contractId : null | string;

    form : FormGroup;

    showFormErrors : boolean = false;

    @ViewChild('fileInputEl')
    fileInputEl : ElementRef<HTMLInputElement>;

    currentDoc : null | CurrentDoc = null;

    uploadDoc : null | UploadDoc = null;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private toastService : ToastService,
        private contractsService : ContractsService,
        private documentsService : DocumentsService,
    ) {
        this.titleService.setTitle('contracts.pg.editor.page_title');
        this.state = 'loading';
    }

    ngOnInit () {
        this.contractId = this.route.snapshot.params['id'] || null;
        this.fetchData();
    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async fetchData () {
        const responses : null | [ null | PGContractResponseData, string[], string[] ] = await Promise.all([
            (
                this.contractId ?
                this.contractsService.fetchPGContract(this.contractId).toPromise() :
                Promise.resolve(null)
            ),
            this.contractsService.fetchGateways().toPromise(),
        ]).catch(() => null);

        console.log(responses);

        if (!responses) {
            this.state = 'error';
            return;
        }

        const contract = responses[0];

        this.createForm(contract);
        await this.updateDoc(contract);
        this.updateGateways(responses[1]);

        this.state = 'ready';
    }

    async updateDoc (contract : null | PGContractResponseData) {
        if (contract) {
            const currentDoc : CurrentDoc = {
                id: contract.document_id,
                name: contract.document_name,
                downloadUrl: null,
            };

            if (contract.document_id) {
                currentDoc.downloadUrl = await this.documentsService.fetchDownloadUrl(contract.document_id).toPromise().catch(() => null);
            }

            this.currentDoc = currentDoc;
        } else {
            this.currentDoc = null;
        }
    }

    updateGateways (gateways : string[]) {
        this.gatewayOptions = [
            {
                value: null,
                display: ''
            },
            ...(gateways || []).map((gateway : string) => ({
                value: gateway,
                display: gateway
            }))
        ];
    }

    deserializeNumber (value : null | number, divider : null | number) : null | number {
        if (typeof value !== 'number') {
            return null;
        }

        if (typeof divider === 'number') {
            value = divFloat(value, divider);
        }

        return value;
    }

    serializeNumber (value : null | number, multiplier : null | number) : null | number {
        if (typeof value !== 'number') {
            return null;
        }

        if (typeof multiplier === 'number') {
            value = mulFloat(value, multiplier);
        }

        return value;
    }

    createForm (contract : null | PGContractResponseData) {
        this.form = this.formBuilder.group({
            name:         [ contract?.name || '', [ Validators.required, Validators.minLength(2) ] ],
            enabled:      [ contract?.enabled === true ],
            gateway:      [ contract?.gateway, [ Validators.required ] ],
            startDate:    [ contract?.start_date, [ Validators.required ] ],
            endDate:      [ contract?.end_date, [ Validators.required ] ],

            tier1Volume:  [ contract?.tier1.volume, [ Validators.required ] ],
            tier1Rate:    [ this.deserializeNumber(contract?.tier1.rate, 1000), [ Validators.required, Validators.min(0), Validators.max(100) ] ],
            tier1Fee:     [ this.deserializeNumber(contract?.tier1.fee, 100), [ Validators.required, Validators.min(0) ] ],
            tier1Minimum: [ this.deserializeNumber(contract?.tier1.minimum, 100), [ Validators.required, Validators.min(0) ] ],

            tier2Volume:  [ contract?.tier2.volume, [ Validators.required ] ],
            tier2Rate:    [ this.deserializeNumber(contract?.tier2.rate, 1000), [ Validators.required, Validators.min(0), Validators.max(100) ] ],
            tier2Fee:     [ this.deserializeNumber(contract?.tier2.fee, 100), [ Validators.required, Validators.min(0) ] ],

            tier3Volume:  [ contract?.tier3.volume, [ Validators.required ] ],
            tier3Rate:    [ this.deserializeNumber(contract?.tier3.rate, 1000), [ Validators.required, Validators.min(0), Validators.max(100) ] ],
            tier3Fee:     [ this.deserializeNumber(contract?.tier3.fee, 100), [ Validators.required, Validators.min(0) ] ],
        });
    }

    updateForm (contract : PGContractResponseData) {
        this.form.reset({
            name:         contract.name,
            enabled:      contract.enabled,
            gateway:      contract.gateway,
            startDate:    contract.start_date,
            endDate:      contract.end_date,

            tier1Volume:  contract.tier1.volume,
            tier1Rate:    this.deserializeNumber(contract.tier1.rate, 1000),
            tier1Fee:     this.deserializeNumber(contract.tier1.fee, 100),
            tier1Minimum: this.deserializeNumber(contract.tier1.minimum, 100),

            tier2Volume:  contract.tier2.volume,
            tier2Rate:    this.deserializeNumber(contract.tier2.rate, 1000),
            tier2Fee:     this.deserializeNumber(contract.tier2.fee, 100),

            tier3Volume:  contract.tier3.volume,
            tier3Rate:    this.deserializeNumber(contract.tier3.rate, 1000),
            tier3Fee:     this.deserializeNumber(contract.tier3.fee, 100),
        }, { emitEvent: true });

        this.form.markAsPristine();
        this.form.markAsUntouched();

        this.showFormErrors = false;
    }

    async uploadFile () : Promise<boolean> {
        if (this.uploadDoc && !this.uploadDoc.isUploaded) {
            const docParams = await this.documentsService.fetchUploadUrl({
                document_name: this.uploadDoc.file.name
            }).toPromise().catch(() => null);

            if (docParams) {
                const isOk = await this.documentsService.uploadFile(
                    docParams.url,
                    this.uploadDoc.file
                );

                // TODO: right way check
                if (isOk) {
                    this.uploadDoc.id = docParams.document_id;
                    this.uploadDoc.isUploaded = true;
                }
            }
        }

        return !this.uploadDoc || this.uploadDoc.isUploaded;
    }

    async onSubmit () {
        if (this.isSubmitting) {
            return;
        }

        if (!this.form.valid) {
            this.showFormErrors = true;
            return;
        }

        this.isSubmitting = true;

        const isUploadOk = await this.uploadFile();

        if (!isUploadOk) {
            this.isSubmitting = false;

            this.toastService.create({
                message: [ 'contracts.pg.editor.upload_failed' ],
                timeout: 6000
            });

            return;
        }

        const documentId = this.uploadDoc?.id || this.currentDoc?.id;
        const formData = this.form.getRawValue();

        const requestData : PGContractRequestData = {
            name: formData.name,
            gateway: formData.gateway,
            start_date: formData.startDate,
            end_date: formData.endDate,
            enabled: formData.enabled,
            document_id: documentId,
            tier1: {
                volume: formData.tier1Volume,
                rate: this.serializeNumber(formData.tier1Rate, 1000),
                fee: this.serializeNumber(formData.tier1Fee, 100),
                minimum: this.serializeNumber(formData.tier1Minimum, 100),
            },
            tier2: {
                volume: formData.tier2Volume,
                rate: this.serializeNumber(formData.tier2Rate, 1000),
                fee: this.serializeNumber(formData.tier2Fee, 100),
                minimum: null,
            },
            tier3: {
                volume: formData.tier3Volume,
                rate: this.serializeNumber(formData.tier3Rate, 1000),
                fee: this.serializeNumber(formData.tier3Fee, 100),
                minimum: null,
            },
        };

        console.log(this.contractId);

        const response : null | PGContractResponseData = await this.makeSaveRequest(this.contractId, requestData);

        if (response) {
            this.contractId = response.id;

            this.updateForm(response);
            await this.updateDoc(response);
            this.updateGateways(response.gateways);
            this.resetFile();

            this.location.replaceState(`/dashboard/contracts/payment-gateway/${ this.contractId }`);

            this.toastService.create({
                message: [ 'contracts.pg.editor.save_success' ]
            });
        } else {
            this.toastService.create({
                message: [ 'contracts.pg.editor.save_failed' ]
            });
        }

        this.isSubmitting = false;
    }

    async makeSaveRequest (contractId : string, requestData : PGContractRequestData) : Promise<null | PGContractResponseData> {
        if (contractId) {
            return await this.contractsService.updatePGContract(contractId, requestData).toPromise().catch(() => null);
        } else {
            return await this.contractsService.createPGContract(requestData).toPromise().catch(() => null);
        }
    }

    resetFile () {
        if (this.fileInputEl) {
            this.fileInputEl.nativeElement.value = '';
            this.uploadDoc = null;
        }
    }

    onSelectFile () {
        this.fileInputEl?.nativeElement.click();
    }

    onFileSelected () {
        this.uploadDoc = {
            id: null,
            isUploaded: false,
            file: this.getSelectedFile()
        };
    }

    getSelectedFile () : null | File {
        return (this.fileInputEl?.nativeElement.files || [])[0] || null;
    }

    onBack () {
        this.router.navigateByUrl('/dashboard/contracts/payment-gateways');
    }
}
