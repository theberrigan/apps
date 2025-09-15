import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
    name: 'mapToolAuthorityNameStates',
    pure: true
})
export class MapToolAuthorityNameStatesPipe implements PipeTransform {

    transform(toll_authority_name: string, ...args: unknown[]): string {
        const stateNames = {
            NTTA: ['Dallas'],
            SUNPASS: ['Florida'],
            FASTRAK: ['California'],
            IPASS: ['Illinois'],
        }
        const statesNamesForTollAuthority = stateNames[toll_authority_name];

        if (statesNamesForTollAuthority && statesNamesForTollAuthority.length > 0) {
            const stateNamesSeparator = ' - ';
            const joinedStatesNames = statesNamesForTollAuthority.join(stateNamesSeparator);

            return joinedStatesNames + stateNamesSeparator + toll_authority_name;
        }
        return toll_authority_name;
    }

}
