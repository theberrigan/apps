import { Injectable } from '@angular/core';
import { CONFIG } from '../../../config/app/dev';
import {HttpErrorResponse} from '@angular/common/http';

const DBG_OBJECT_NAME = 'tnp';
const DBG_OBJECT_HELP_CMD = 'help';

interface DebugOptions {
    help? : string
}

@Injectable({
    providedIn: 'root'
})
export class DebugService {
    private readonly dbgObject : any = {};

    private readonly isDebug : boolean = CONFIG.isDebug;

    private readonly helpDatabase : any[] = [];

    constructor () {
        if (this.isDebug) {
            Object.defineProperty(this.dbgObject, DBG_OBJECT_HELP_CMD, {
                value: () => this.showHelp(),
                configurable: false,
            });

            Object.defineProperty(window, DBG_OBJECT_NAME, {
                value: this.dbgObject,
                configurable: false,
            });

            console.warn(`Type '${ DBG_OBJECT_NAME }.${ DBG_OBJECT_HELP_CMD }()' to see debug options`);
        }
    }

    register (key : string, obj : any, options? : DebugOptions) {
        if (!this.isDebug) {
            return;
        }

        options = options || {};

        const helpMessage : string = (options.help || '').trim();

        const existingIndex = this.helpDatabase.findIndex(item => item.key === key);

        if (existingIndex >= 0) {
            this.helpDatabase.splice(existingIndex, 1);
        }

        this.helpDatabase.push({
            key,
            helpMessage,
            isFunc: typeof obj === 'function'
        });

        this.helpDatabase.sort((a, b) => String(a.key).localeCompare(String(b.key)));

        Object.defineProperty(this.dbgObject, key, {
            value: obj,
            configurable: false
        });
    }

    showHelp () {
        const messages = this.helpDatabase.map(item => {
            return `– tnp.${ item.key }${ item.isFunc ? '()' : '' }${ item.helpMessage ? ` - ${ item.helpMessage }` : '' }`;
        });

        console.warn(`Debug functions:\n${ messages.join('\n') }`);
    }

    logNetworkError (error : HttpErrorResponse, methodName : string = '') {
        if (error.error) {
            console.warn(`${ methodName } error:\n\t${ error.url }\n\t${ error.error.status_code } ${ error.error.status } ${ error.error.message }\n\tError object:`, error);
        } else {
            console.warn(`${ methodName } error:\n\t${ error.url }\n\t${ error.status } ${ error.statusText } ${ error.name } ${ error.message }\n\tError object:`, error);
        }
    }
}
