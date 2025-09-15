import {
    Component,
    ViewEncapsulation
} from '@angular/core';

@Component({
    selector: 'loader',
    exportAs: 'loader',
    templateUrl: './loader.component.html',
    styleUrls: [ './loader.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'loader'
    }
})
export class LoaderComponent {

}
