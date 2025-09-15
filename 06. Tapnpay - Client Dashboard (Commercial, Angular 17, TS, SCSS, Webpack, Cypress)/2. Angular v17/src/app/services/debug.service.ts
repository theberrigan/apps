import {Injectable} from '@angular/core';
import {CONFIG} from '../../../config/app/dev';
import { HttpErrorResponse } from '@angular/common/http';
import {UserService} from "./user.service";
import {take} from "rxjs/operators";

const DBG_OBJECT_NAME = 'tnp';
const DBG_OBJECT_HELP_CMD = 'help';

interface DebugOptions {
    help?: string
}

@Injectable({
    providedIn: 'root'
})
export class DebugService {
    private readonly dbgObject: any = {};

    private readonly isDebug: boolean = CONFIG.isDebug;

    private readonly helpDatabase: any[] = [];

    constructor(private userService: UserService) {
        if (this.isDebug) {
            this.initWindowHelpConsoleCommand();

            this.initWindowTNPConsoleCommand();

            console.warn(`Type '${DBG_OBJECT_NAME}.${DBG_OBJECT_HELP_CMD}()' to see debug options`);
        }
    }

    private initWindowHelpConsoleCommand() {
        Object.defineProperty(this.dbgObject, DBG_OBJECT_HELP_CMD, {
            value: () => this.showHelp(),
            configurable: false,
        });
    }

    private initWindowTNPConsoleCommand() {
        Object.defineProperty(window, DBG_OBJECT_NAME, {
            value: this.dbgObject,
            configurable: false,
        });
    }

    public initConsoleCommands(): void {
        this.registerNewConsoleCommand('genInvoices', async (phone?: string) => {
            await this.userService.generateInvoices(phone).toPromise().catch(() => null);
        }, {help: 'Generate invoices for fleet model'});

        this.registerNewConsoleCommand('lockByPhone', async (phone: string, status: string = 'ACCOUNT_DEBT_LOCK') => {
            await this.userService.lockAccount(phone, status).toPromise().catch(() => null);
        }, {help: 'Lock account'});

        this.registerNewConsoleCommand('getPinForAcc', async (phone: string) => {
            this.userService.getTestAccountPin(phone).pipe(
                take(1)
            ).subscribe((pin: string) => {
                console.warn(`Test account: ${phone} / ${pin}`);
            });
        }, {help: 'Get PIN'});

        this.registerNewConsoleCommand('setLang', (lang: string) => {
            return this.userService.setAppLang(lang);
        }, {help: `Change application language (${(this.userService.getLangNames())})`});
    }

    registerNewConsoleCommand(commandName: string, commandFunction: any, options?: DebugOptions) {
        if (!this.isDebug) {
            return;
        }

        options = options || {};

        const helpMessage: string = (options.help || '').trim();

        const existingIndex = this.helpDatabase.findIndex(item => item.key === commandName);

        if (existingIndex >= 0) {
            this.helpDatabase.splice(existingIndex, 1);
        }

        this.helpDatabase.push({
            key: commandName,
            helpMessage,
            isFunc: typeof commandFunction === 'function'
        });

        this.helpDatabase.sort((a, b) => String(a.key).localeCompare(String(b.key)));

        if (!this.dbgObject[commandName]) {
            Object.defineProperty(this.dbgObject, commandName, {
                value: commandFunction,
                configurable: false
            });
        }
    }

    showHelp() {
        const messages = this.helpDatabase.map(item => {
            return `– tnp.${item.key}${item.isFunc ? '()' : ''}${item.helpMessage ? ` - ${item.helpMessage}` : ''}`;
        });

        console.warn(`Debug functions:\n${messages.join('\n')}`);
    }
}
