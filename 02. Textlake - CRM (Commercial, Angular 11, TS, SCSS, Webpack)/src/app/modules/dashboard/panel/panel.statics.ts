import { cloneDeep } from 'lodash';
import { TaskStatus } from './panel.types';

const TASKS_STATUSES : TaskStatus[] = [
    {
        id: 0,
        display: 'panel.tasks.statuses.open',
        isChecked: true,
        isVisible: true
    },
    {
        id: 1,
        display: 'panel.tasks.statuses.assigned',
        isChecked: true,
        isVisible: false
    },
    {
        id: 2,
        display: 'panel.tasks.statuses.closed',
        isChecked: false,
        isVisible: true
    }
];

export const NOTIFICATIONS_TO_LOAD = 15;

export const NOTIFICATIONS_VISIBLE_MAX = 25;

export const TASKS_TO_LOAD = 15;

export const getTaskStatuses : () => TaskStatus[] = () => {
    return cloneDeep(TASKS_STATUSES) as TaskStatus[];
};
