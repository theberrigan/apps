import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
    name: 'isListEmpty'
})
export class IsListEmptyPipe implements PipeTransform {

    transform(value: unknown, ...args: unknown[]): boolean {
        if (Array.isArray(value)) {
            return value.length === 0;
        }
        return false;
    }

}
