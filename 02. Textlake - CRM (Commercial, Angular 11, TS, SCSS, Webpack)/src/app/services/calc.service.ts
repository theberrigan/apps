import {Injectable} from '@angular/core';
import { isFinite } from '../lib/utils';

export type RoundingRule = 'ROUND_UP' | 'ROUND_DOWN' | 'ROUND_CEILING' | 'ROUND_FLOOR' | 'ROUND_HALF_UP' | 'ROUND_HALF_DOWN' | 'ROUND_HALF_EVEN';

@Injectable({
    providedIn: 'root'
})
export class CalcService {

    public round (num : number, rule : RoundingRule, fractionLength : number = 0) {
        if (!isFinite(num)) {
            return num;
        }

        const sign = (num < 0 ? -1 : 1);

        switch (rule) {
            case 'ROUND_UP':
                return sign * Math.ceil(Math.abs(num));
            case 'ROUND_DOWN':
                return sign * Math.floor(Math.abs(num));
            case 'ROUND_CEILING':
                return Math.ceil(num);
            case 'ROUND_FLOOR':
                return Math.floor(num);
            case 'ROUND_HALF_UP':
                return sign * Math.floor(Math.abs(num) + 0.5);
            case 'ROUND_HALF_DOWN':
                return sign * Math.ceil(Math.abs(num) - 0.5);
            case 'ROUND_HALF_EVEN':
                const fracFactor = Math.pow(10, fractionLength);
                num = +((fractionLength ? num * fracFactor : num).toFixed(8)); // Avoid rounding errors
                const numFloor = Math.floor(num);
                const fraction = num - numFloor;
                const tinyNum = 1e-8; // Allow for rounding errors in fraction
                const result = (fraction > (0.5 - tinyNum) && fraction < (0.5 + tinyNum)) ?
                    ((numFloor % 2 === 0) ? numFloor : numFloor + 1) : Math.round(num);
                return fractionLength ? result / fracFactor : result;
        }
    }
}
