import {Pipe, PipeTransform} from '@angular/core';

const replacementMap = {
    "TXHUB": "EZTag, TollTag, TxTag",
    "IPASS": "IPass, E-ZPass"
};

@Pipe({
    name: 'taNameToShow'
})
export class TaNameToShowPipe implements PipeTransform {

    transform(value: unknown): string {
        const taName = value as string;
        const replacement = replacementMap[taName];
        if (replacement) {
            return replacement.toUpperCase();
        }
        return taName.toUpperCase();
    }

}
