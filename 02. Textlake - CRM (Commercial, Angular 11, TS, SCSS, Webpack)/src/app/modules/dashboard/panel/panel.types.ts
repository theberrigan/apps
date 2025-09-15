export class TaskStatus {
    id : number;
    display : string;     // i18n key of status name
    isChecked : boolean;  // is checked in task manager by default
    isVisible : boolean;  // is visible in the task manager
}

export type TasksPagingState = 'hidden' | 'button' | 'loading';
export type TasksState = 'loading' | 'error' | 'ok';
export type NotificationsState = 'loading' | 'error' | 'ok';
export type PanelButtonMarkType = null | 'dot' | 'counter';
