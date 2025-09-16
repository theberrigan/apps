import { CanDeactivate } from '@angular/router';

export interface ConfirmDiscard {
    canDeactivate : () => boolean | Promise<boolean>;
}

export class DiscardGuard implements CanDeactivate<ConfirmDiscard> {
    public canDeactivate (component : ConfirmDiscard) : boolean | Promise<boolean> {
        return component.canDeactivate();
    }
}
