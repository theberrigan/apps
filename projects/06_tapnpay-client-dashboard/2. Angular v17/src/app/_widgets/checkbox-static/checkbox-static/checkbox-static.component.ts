import {
    Component, HostBinding, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

@Component({
    selector: 'checkbox-static',
    exportAs: 'checkboxStatic',
    templateUrl: './checkbox-static.component.html',
    styleUrls: [ './checkbox-static.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'checkbox-static'
    }
})
export class CheckboxStaticComponent implements OnInit, OnDestroy {
    @Input()
    @HostBinding('class.checkbox-static_disabled')
    public isDisabled : boolean = false;

    @Input()
    @HostBinding('class.checkbox-static_checked')
    public isChecked : boolean = false;

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }
}
