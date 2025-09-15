import {Component, Input, OnChanges, SimpleChanges} from '@angular/core';

@Component({
    selector: 'app-no-items',
    templateUrl: './no-items.component.html',
    styleUrls: ['./no-items.component.scss']
})
export class NoItemsComponent implements OnChanges {

    @Input() messageType: 'usual' | 'rental' = 'usual';
    usualMessageToDisplay: string = 'No personal car plates added yet';
    rentalMessageToDisplay: string = 'No rental car plates added yet';
    textToDisplay = this.usualMessageToDisplay;

    ngOnChanges(changes: SimpleChanges) {
        if (changes.messageType.currentValue === 'rental') {
            this.textToDisplay = this.rentalMessageToDisplay;
        } else {
            this.textToDisplay = this.usualMessageToDisplay;
        }
    }
}
