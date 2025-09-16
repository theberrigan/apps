import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface NavPipeMessage {
    action : string;
}

@Injectable({
    providedIn: 'root'
})
export class NavService {
    navMessagePipe = new Subject<NavPipeMessage>();

    constructor () {

    }
}
