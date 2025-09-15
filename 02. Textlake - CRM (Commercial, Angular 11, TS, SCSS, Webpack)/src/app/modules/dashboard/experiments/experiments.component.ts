import {ChangeDetectorRef, Component, OnChanges, OnInit, SimpleChanges, ViewEncapsulation} from '@angular/core';
import {FormBuilder} from '@angular/forms';
import {ToastService} from '../../../services/toast.service';

@Component({
    selector: 'experiments',
    templateUrl: './experiments.component.html',
    styleUrls: [ './experiments.component.scss' ],
    encapsulation: ViewEncapsulation.None
})
export class ExperimentsComponent implements OnInit, OnChanges {
    constructor (
        private cdr : ChangeDetectorRef,
        private formBuilder : FormBuilder,
        private toastService : ToastService
    ) {}

    // popup_width-by-content
    //

    ngOnInit () {

    }

    public ngOnChanges (changes : SimpleChanges) : void {

    }

    public showToast () : void {
        this.toastService.create({ message: ("hello! ").repeat(Math.random() * (15 - 1) + 1) });
    }
}
