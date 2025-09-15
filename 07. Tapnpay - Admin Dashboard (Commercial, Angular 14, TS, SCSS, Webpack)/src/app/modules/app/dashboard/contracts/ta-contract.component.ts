import {
    ChangeDetectionStrategy,
    Component, ElementRef,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {Location} from '@angular/common';
import {ToastService} from '../../../../services/toast.service';
import {
    ContractContact,
    ContractsService, TAContractRequestData, TAContractResponseData
} from '../../../../services/contracts.service';
import {divFloat, mulFloat} from '../../../../lib/utils';
import {TAListItem, TAService} from '../../../../services/ta.service';
import {DocumentsService} from '../../../../services/documents.service';


type State = 'loading' | 'ready' | 'error';

interface SelectOption {
    value : null | number | string;
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

// TODO:
// fetchCustomers endpoint
// createCustomer endpoint
// add customer to the from
// saas fee structure options endpoint?
// + minimum 100


@Component({
    selector: 'ta-contract',
    templateUrl: './ta-contract.component.html',
    styleUrls: [ './ta-contract.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'ta-contract'
    },
})
export class TAContractComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    state : State = 'loading';

    isSubmitting : boolean = false;

    contractId : null | string;

    form : FormGroup;

    showFormErrors : boolean = false;

    customerOptions : SelectOption[];

    saasFeeStructureOptions : SelectOption[];

    isCustomerPopupVisible : boolean = false;

    isCustomerNameValid : boolean = false;

    customerName : string = '';

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
        private taService : TAService,
        private documentsService : DocumentsService,
    ) {
        this.titleService.setTitle('contracts.ta.editor.page_title');
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
        const responses : null | [ null | TAContractResponseData, string[], TAListItem[] ] = await Promise.all([
            (
                this.contractId ?
                this.contractsService.fetchTAContract(this.contractId).toPromise() :
                Promise.resolve(null)
            ),
            this.contractsService.fetchSaasFeeStructures().toPromise(),
            this.taService.fetchTAs().toPromise(),
        ]).catch(() => null);

        console.log(responses);

        if (!responses) {
            this.state = 'error';
            return;
        }

        const contract = responses[0];

        this.createForm(contract);
        await this.updateDoc(contract);
        this.updateSaasFeeStructures(responses[1]);
        this.updateCustomers(responses[2]);

        this.state = 'ready';
    }

    async updateDoc (contract : null | TAContractResponseData) {
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

    updateSaasFeeStructures (structures : string[]) {
        this.saasFeeStructureOptions = [
            {
                value: null,
                display: ''
            },
            ...(structures || []).map((structure : string) => ({
                value: structure,
                display: structure
            }))
        ];
    }

    updateCustomers (customers : TAListItem[]) {
        this.customerOptions = [
            {
                value: null,
                display: ''
            },
            ...(customers || []).map((customer : TAListItem) => ({
                value: customer.id,
                display: customer.display_name
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

    createForm (contract : null | TAContractResponseData) {
        this.form = this.formBuilder.group({
            name:             [ contract?.name || '', [ Validators.required, Validators.minLength(2) ] ],
            customerId:       [ contract?.toll_authority_id, [ Validators.required ] ],
            startDate:        [ contract?.start_date, [ Validators.required ] ],
            endDate:          [ contract?.end_date, [ Validators.required ] ],
            enabled:          [ contract?.enabled === true ],
            apCarryingDays:   [ contract?.ap_carrying_days, [ Validators.required, Validators.min(0) ] ],
            saasFeeStructure: [ contract?.saas_fee_structure, [ Validators.required ] ],
            saasFeeAmount:    [ this.deserializeNumber(contract?.saas_fee_amount, 100), [ Validators.required, Validators.min(0) ] ],

            dcbTier1Volume: [ contract?.dcb_tier1.volume, [ Validators.required ] ],
            dcbTier1Rate:   [ this.deserializeNumber(contract?.dcb_tier1.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            dcbTier2Volume: [ contract?.dcb_tier2.volume, [ Validators.required ] ],
            dcbTier2Rate:   [ this.deserializeNumber(contract?.dcb_tier2.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            dcbTier3Rate:   [ this.deserializeNumber(contract?.dcb_tier3.rate, 1000), [ Validators.required, Validators.min(0) ] ],

            creditTier1Volume: [ contract?.credit_card_tier1.volume, [ Validators.required ] ],
            creditTier1Rate:   [ this.deserializeNumber(contract?.credit_card_tier1.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            creditTier2Volume: [ contract?.credit_card_tier2.volume, [ Validators.required ] ],
            creditTier2Rate:   [ this.deserializeNumber(contract?.credit_card_tier2.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            creditTier3Rate:   [ this.deserializeNumber(contract?.credit_card_tier3.rate, 1000), [ Validators.required, Validators.min(0) ] ],

            debitTier1Volume: [ contract?.debit_card_tier1.volume, [ Validators.required ] ],
            debitTier1Rate:   [ this.deserializeNumber(contract?.debit_card_tier1.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            debitTier2Volume: [ contract?.debit_card_tier2.volume, [ Validators.required ] ],
            debitTier2Rate:   [ this.deserializeNumber(contract?.debit_card_tier2.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            debitTier3Rate:   [ this.deserializeNumber(contract?.debit_card_tier3.rate, 1000), [ Validators.required, Validators.min(0) ] ],

            walletTier1Volume: [ contract?.wallet_tier1.volume, [ Validators.required ] ],
            walletTier1Rate:   [ this.deserializeNumber(contract?.wallet_tier1.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            walletTier2Volume: [ contract?.wallet_tier2.volume, [ Validators.required ] ],
            walletTier2Rate:   [ this.deserializeNumber(contract?.wallet_tier2.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            walletTier3Rate:   [ this.deserializeNumber(contract?.wallet_tier3.rate, 1000), [ Validators.required, Validators.min(0) ] ],

            paypalTier1Volume: [ contract?.paypal_tier1.volume, [ Validators.required ] ],
            paypalTier1Rate:   [ this.deserializeNumber(contract?.paypal_tier1.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            paypalTier2Volume: [ contract?.paypal_tier2.volume, [ Validators.required ] ],
            paypalTier2Rate:   [ this.deserializeNumber(contract?.paypal_tier2.rate, 1000), [ Validators.required, Validators.min(0) ] ],
            paypalTier3Rate:   [ this.deserializeNumber(contract?.paypal_tier3.rate, 1000), [ Validators.required, Validators.min(0) ] ],

            customerContactName:  [ contract?.customer_contact?.name || '', [ Validators.required, Validators.minLength(2) ] ],
            customerContactPhone: [ contract?.customer_contact?.phone || '', [ Validators.required, Validators.minLength(2) ] ],
            customerContactEmail: [ contract?.customer_contact?.email || '', [ Validators.required, Validators.email ] ],
            paypalContactName:  [ contract?.paypal_contact?.name || '', [ Validators.required, Validators.minLength(2) ] ],
            paypalContactPhone: [ contract?.paypal_contact?.phone || '', [ Validators.required, Validators.minLength(2) ] ],
            paypalContactEmail: [ contract?.paypal_contact?.email || '', [ Validators.required, Validators.email ] ],
            tnpContactName:       [ contract?.tnp_contact?.name || '', [ Validators.required, Validators.minLength(2) ] ],
            tnpContactPhone:      [ contract?.tnp_contact?.phone || '', [ Validators.required, Validators.minLength(2) ] ],
            tnpContactEmail:      [ contract?.tnp_contact?.email || '', [ Validators.required, Validators.email ] ],
        });
    }

    updateForm (contract : TAContractResponseData) {
        this.form.reset({
            name:             contract.name || '',
            customerId:       contract.toll_authority_id || null,
            startDate:        contract.start_date || null,
            endDate:          contract.end_date || null,
            enabled:          contract.enabled === true,
            apCarryingDays:   contract.ap_carrying_days,
            saasFeeStructure: contract.saas_fee_structure,
            saasFeeAmount:    this.deserializeNumber(contract.saas_fee_amount, 100),

            dcbTier1Volume: contract.dcb_tier1.volume,
            dcbTier1Rate:   this.deserializeNumber(contract.dcb_tier1.rate, 1000),
            dcbTier2Volume: contract.dcb_tier2.volume,
            dcbTier2Rate:   this.deserializeNumber(contract.dcb_tier2.rate, 1000),
            dcbTier3Rate:   this.deserializeNumber(contract.dcb_tier3.rate, 1000),

            creditTier1Volume: contract.credit_card_tier1.volume,
            creditTier1Rate:   this.deserializeNumber(contract.credit_card_tier1.rate, 1000),
            creditTier2Volume: contract.credit_card_tier2.volume,
            creditTier2Rate:   this.deserializeNumber(contract.credit_card_tier2.rate, 1000),
            creditTier3Rate:   this.deserializeNumber(contract.credit_card_tier3.rate, 1000),

            debitTier1Volume: contract.debit_card_tier1.volume,
            debitTier1Rate:   this.deserializeNumber(contract.debit_card_tier1.rate, 1000),
            debitTier2Volume: contract.debit_card_tier2.volume,
            debitTier2Rate:   this.deserializeNumber(contract.debit_card_tier2.rate, 1000),
            debitTier3Rate:   this.deserializeNumber(contract.debit_card_tier3.rate, 1000),

            walletTier1Volume: contract.wallet_tier1.volume,
            walletTier1Rate:   this.deserializeNumber(contract.wallet_tier1.rate, 1000),
            walletTier2Volume: contract.wallet_tier2.volume,
            walletTier2Rate:   this.deserializeNumber(contract.wallet_tier2.rate, 1000),
            walletTier3Rate:   this.deserializeNumber(contract.wallet_tier3.rate, 1000),

            paypalTier1Volume: contract.paypal_tier1.volume,
            paypalTier1Rate:   this.deserializeNumber(contract.paypal_tier1.rate, 1000),
            paypalTier2Volume: contract.paypal_tier2.volume,
            paypalTier2Rate:   this.deserializeNumber(contract.paypal_tier2.rate, 1000),
            paypalTier3Rate:   this.deserializeNumber(contract.paypal_tier3.rate, 1000),

            customerContactName:  contract.customer_contact?.name || '',
            customerContactPhone: contract.customer_contact?.phone || '',
            customerContactEmail: contract.customer_contact?.email || '',

            paypalContactName:  contract.paypal_contact?.name || '',
            paypalContactPhone: contract.paypal_contact?.phone || '',
            paypalContactEmail: contract.paypal_contact?.email || '',

            tnpContactName:       contract.tnp_contact?.name || '',
            tnpContactPhone:      contract.tnp_contact?.phone || '',
            tnpContactEmail:      contract.tnp_contact?.email || '',
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
                message: [ 'contracts.ta.editor.upload_failed' ],
                timeout: 6000
            });

            return;
        }

        const documentId = this.uploadDoc?.id || this.currentDoc?.id;
        const formData = this.form.getRawValue();

        const requestData : TAContractRequestData = {
            name: formData.name,
            start_date: formData.startDate,
            end_date: formData.endDate,
            enabled: formData.enabled,
            toll_authority_id: formData.customerId,
            ap_carrying_days: formData.apCarryingDays,
            saas_fee_structure: formData.saasFeeStructure,
            saas_fee_amount: this.serializeNumber(formData.saasFeeAmount, 100),
            document_id: documentId,
            dcb_tier1: {
                volume: formData.dcbTier1Volume,
                rate: this.serializeNumber(formData.dcbTier1Rate, 1000),
                fee: null,
                minimum: null,
            },
            dcb_tier2: {
                volume: formData.dcbTier2Volume,
                rate: this.serializeNumber(formData.dcbTier2Rate, 1000),
                fee: null,
                minimum: null,
            },
            dcb_tier3: {
                volume: null,
                rate: this.serializeNumber(formData.dcbTier3Rate, 1000),
                fee: null,
                minimum: null,
            },
            credit_card_tier1: {
                volume: formData.creditTier1Volume,
                rate: this.serializeNumber(formData.creditTier1Rate, 1000),
                fee: null,
                minimum: null,
            },
            credit_card_tier2: {
                volume: formData.creditTier2Volume,
                rate: this.serializeNumber(formData.creditTier2Rate, 1000),
                fee: null,
                minimum: null,
            },
            credit_card_tier3: {
                volume: null,
                rate: this.serializeNumber(formData.creditTier3Rate, 1000),
                fee: null,
                minimum: null,
            },
            debit_card_tier1: {
                volume: formData.debitTier1Volume,
                rate: this.serializeNumber(formData.debitTier1Rate, 1000),
                fee: null,
                minimum: null,
            },
            debit_card_tier2: {
                volume: formData.debitTier2Volume,
                rate: this.serializeNumber(formData.debitTier2Rate, 1000),
                fee: null,
                minimum: null,
            },
            debit_card_tier3: {
                volume: null,
                rate: this.serializeNumber(formData.debitTier3Rate, 1000),
                fee: null,
                minimum: null,
            },
            wallet_tier1: {
                volume: formData.walletTier1Volume,
                rate: this.serializeNumber(formData.walletTier1Rate, 1000),
                fee: null,
                minimum: null,
            },
            wallet_tier2: {
                volume: formData.walletTier2Volume,
                rate: this.serializeNumber(formData.walletTier2Rate, 1000),
                fee: null,
                minimum: null,
            },
            wallet_tier3: {
                volume: null,
                rate: this.serializeNumber(formData.walletTier3Rate, 1000),
                fee: null,
                minimum: null,
            },
            paypal_tier1: {
                volume: formData.paypalTier1Volume,
                rate: this.serializeNumber(formData.paypalTier1Rate, 1000),
                fee: null,
                minimum: null,
            },
            paypal_tier2: {
                volume: formData.paypalTier2Volume,
                rate: this.serializeNumber(formData.paypalTier2Rate, 1000),
                fee: null,
                minimum: null,
            },
            paypal_tier3: {
                volume: null,
                rate: this.serializeNumber(formData.paypalTier3Rate, 1000),
                fee: null,
                minimum: null,
            },
            customer_contact: {
                name: formData.customerContactName,
                phone: formData.customerContactPhone,
                email: formData.customerContactEmail,
            },
            paypal_contact: {
                name: formData.paypalContactName,
                phone: formData.paypalContactPhone,
                email: formData.paypalContactEmail,
            },
            tnp_contact: {
                name: formData.tnpContactName,
                phone: formData.tnpContactPhone,
                email: formData.tnpContactEmail,
            },
        };

        console.log(this.contractId);

        const response : null | TAContractResponseData = await this.makeSaveRequest(this.contractId, requestData);

        if (response) {
            this.contractId = response.id;

            this.updateForm(response);
            await this.updateDoc(response);
            this.resetFile();

            this.location.replaceState(`/dashboard/contracts/toll-authority/${ this.contractId }`);

            this.toastService.create({
                message: [ 'contracts.ta.editor.save_success' ]
            });
        } else {
            this.toastService.create({
                message: [ 'contracts.ta.editor.save_failed' ]
            });
        }

        this.isSubmitting = false;
    }

    async makeSaveRequest (contractId : string, requestData : TAContractRequestData) : Promise<null | TAContractResponseData> {
        if (contractId) {
            return await this.contractsService.updateTAContract(contractId, requestData).toPromise().catch(() => null);
        } else {
            return await this.contractsService.createTAContract(requestData).toPromise().catch(() => null);
        }
    }

    onCreateCustomer () {
        this.customerName = '';
        this.isCustomerNameValid = false;
        this.isCustomerPopupVisible = true;
    }

    onCancelCreateCustomer () {
        this.hideCustomerPopup();
    }

    async onConfirmCreateCustomer () {
        if (this.isSubmitting || !this.isCustomerNameValid) {
            return;
        }

        this.isSubmitting = true;

        const name = (this.customerName || '').trim();
        const result = await this.taService.createTA({ name }).toPromise().catch(() => null);

        if (result) {
            const customers = await this.taService.fetchTAs().toPromise();
            this.updateCustomers(customers);
            this.hideCustomerPopup();

            this.toastService.create({
                message: [ 'contracts.ta.editor.create_customer_success' ],
                timeout: 9000
            });
        } else {
            this.toastService.create({
                message: [ 'contracts.ta.editor.create_customer_error' ],
                timeout: 9000
            });
        }

        this.isSubmitting = false;
    }

    hideCustomerPopup () {
        this.isCustomerPopupVisible = false;
    }

    validateCustomerName () {
        this.isCustomerNameValid = !!(this.customerName || '').trim();
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
        this.router.navigateByUrl('/dashboard/contracts/toll-authorities');
    }
}
