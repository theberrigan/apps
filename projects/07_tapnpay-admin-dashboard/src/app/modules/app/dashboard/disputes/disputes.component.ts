import {
    ChangeDetectionStrategy,
    Component, ElementRef, HostListener, Input,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {ToastService} from '../../../../services/toast.service';
import {DisputesService} from '../../../../services/disputes.service';


@Component({
    selector: 'disputes',
    templateUrl: './disputes.component.html',
    styleUrls: [ './disputes.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'disputes'
    },
})
export class DisputesComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    isDropzoneVisible : boolean = false;

    isUploading : boolean = false;

    @ViewChild('uploadForm')
    uploadForm : ElementRef;

    @ViewChild('uploadInput')
    uploadInput : ElementRef;

    messages : string[];

    constructor (
        private titleService : TitleService,
        private toastService : ToastService,
        private disputesService : DisputesService,
    ) {
        this.titleService.setTitle('disputes.page_title');
    }

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    @HostListener('document:dragenter', [ '$event' ])
    onDocDragEnter (e : DragEvent) {
        e.stopPropagation();
        e.preventDefault();

        if (this.isUploading) {
            return;
        }

        const items : DataTransferItem[] = Array.from(e.dataTransfer.items || []);

        if (items.some(item => item.kind === 'file') === false) {
            return;
        }

        this.isDropzoneVisible = true;
    }

    onDropzoneDragOver (e) {
        e.stopPropagation();
        e.preventDefault();
        // set dropEffect to 'copy' to fire 'drop' event later
        e.dataTransfer.dropEffect = 'copy';
    }

    onDropzoneDragEnter (e) {
        e.stopPropagation();
        e.preventDefault();
    }

    onDropzoneDragLeave (e) {
        e.stopPropagation();
        e.preventDefault();

        this.isDropzoneVisible = false;
    }

    onFileDrop (e) {
        if (this.isUploading) {
            return;
        }

        e.stopPropagation();
        e.preventDefault();

        this.isDropzoneVisible = false;

        const file : File  = (e?.dataTransfer?.files || [])[0];
        this.uploadFile(file);
    }

    onFileChange () {
        const file : File  = (this.uploadInput?.nativeElement?.files || [])[0];
        this.uploadForm?.nativeElement?.reset();
        this.uploadFile(file);
    }

    async uploadFile (file : File) {
        if (this.isUploading || !file) {
            return;
        }

        this.isUploading = true;
        this.messages = null;

        const messages = await this.disputesService.uploadFile(file).toPromise().catch(() => [
            'An error occurred while uploading the file'
        ]);

        this.isUploading = false;

        if (messages.length === 0) {
            this.toastService.create({
                message: [ 'disputes.upload_success' ],
                timeout: 5000
            });
        } else {
            this.messages = messages;
        }
    }

    onDecoDropzoneClick () {
        if (this.isUploading) {
            return;
        }

        this.uploadInput.nativeElement?.click();
    }
}
