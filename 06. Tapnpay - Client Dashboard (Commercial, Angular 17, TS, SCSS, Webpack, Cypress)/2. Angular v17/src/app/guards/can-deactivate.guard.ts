

export interface ConfirmDiscard {
    canDeactivate : () => boolean | Promise<boolean>;
}

export class CanDeactivateGuard  {
    public canDeactivate (component : ConfirmDiscard) : boolean | Promise<boolean> {
        return component.canDeactivate();
    }
}
