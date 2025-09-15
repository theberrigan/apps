import re, os

COMPONENTS_LIST = [
    [ 'mailbox',           'settings.mailboxes.page_title', 'settings.mailboxes.mailboxes__header', None, 'settings.manage_mailboxes__link', 'settings:mailbox' ],
    [ 'roles',             'settings.roles.page_title', 'settings.roles.roles__header', None, 'settings.manage_user_roles__link', 'settings:roles' ],
    [ 'currencies',        'settings.currencies.page_title', 'settings.currencies.currencies__header', 'settings.currencies.save__button', 'settings.manage_currencies__link', 'settings:currencies' ],
    [ 'company',           'settings.company.page_title', 'settings.company.company__header', 'settings.company.save__button', 'settings.company_profile__link', 'settings:company-profile' ],
    [ 'services',          'settings.services.list.page_title', 'settings.services.list.page_header', None, 'settings.manage_services__link', 'settings:services' ],
    [ 'rates',             'settings.rates.list.page_title', 'settings.rates.list.page_header', None, 'settings.manage_rates__link', 'settings:rates' ],
    [ 'taxes',             'settings.taxes.page_title', 'settings.taxes.page_header', None, 'settings.manage_taxes__link', 'settings:taxes' ],
    [ 'invitations',       'settings.invitations.list.page_title', 'settings.invitations.list.page_header', None, 'settings.manage_invitations__link', 'settings:invitations' ],
    [ 'payment-providers', 'settings.payment_providers.page_title', 'settings.payment_providers.page_header', 'settings.payment_providers.save', 'settings.manage_payment__link', 'settings:payment-providers' ],
    [ 'subscriptions',     'subs.page__title', 'subs.subscription__header', None, 'settings.subscriptions__link', 'settings:subscriptions' ],
]

COMPONENT_SRC_TPL = '''import {Component, OnDestroy, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';

@Component({
    selector: '%%component-dash-name%%',
    templateUrl: './%%component-dash-name%%.component.html',
    styleUrls: [ './%%component-dash-name%%.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': '%%component-html-class-name%%',
    }
})
export class %%component-name%% implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

<!--HAS_SAVE_BTN-->
    public isSaving : boolean = false;

<!--/HAS_SAVE_BTN-->
    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('%%component-page-title%%');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {

    }

<!--HAS_SAVE_BTN-->
    public onSave () : void {
        if (this.isSaving) {
            return;
        }
    }

<!--/HAS_SAVE_BTN-->
    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

'''

COMPONENT_HTML_TPL = '''<fieldset [disabled]="isSaving">
    <action-panel>
        <div class="action-panel__primary">
            <button class="action-panel__back" type="button" (click)="goBack()">
                <svg xmlns="http://www.w3.org/2000/svg" height="16px" width="19px" viewBox="0 0 19 16">
                    <polygon style="fill: currentColor;" points="18.4 8.7 3.8 8.7 9.1 14 7.7 15.4 0 7.7 7.7 0 9.1 1.4 3.8 6.7 18.4 6.7 18.4 8.7"></polygon>
                </svg>
            </button>
            <h1 class="action-panel__header">{{ '%%component-page-header%%' | translate }}</h1>
        </div>
        <div class="action-panel__secondary">
<!--HAS_SAVE_BTN-->
            <div class="action-panel__item">
                <button type="button" class="button button_regular button_blue"
                    [isProgress]="isSaving"
                    (click)="onSave()"
                >
                    <span class="button__caption">{{ '%%component-save-button%%' | translate }}</span>
                </button>
            </div>
<!--/HAS_SAVE_BTN-->        </div>
    </action-panel>
</fieldset>'''

COMPONENT_SCSS_TPL = '''@import '../../../../../assets/css/definitions.scss';

.%%component-html-class-name%% {
    display: block;
}'''

COMPONENT_SETTINGS_ITEM_TPL = '''    <a routerLink="/dashboard/settings/%%component-dash-name%%" class="settings__list-item" *ngIf="isItemVisible('%%settings-item-feature%%')">
        <svg xmlns="http://www.w3.org/2000/svg" width="70" height="70" viewBox="0 0 70 70" class="settings__list-item-icon">

        </svg>
        <div class="settings__list-item-caption">{{ '%%settings-item-caption%%' | translate }}</div>
    </a>'''

COMPONENT_ROUTE_TPL = '''            {
                path: '%%component-dash-name%%',
                component: %%component-name%%,
            },'''

def camelize (input):
    output = ''
    wasDash = False

    for i, c in enumerate(input):
        if c == '-':
            wasDash = True
            continue
        output += c.upper() if (i == 0 or wasDash) else c.lower()
        wasDash = False

    return output

def fillPlaceholders (tpl, placeholders):
    for pKey, pValue in placeholders.items():
        if pValue:
            tpl = tpl.replace('%%' + pKey + '%%', pValue)
    return tpl

def replceSaveButton (tpl, hasSaveButton):
    if hasSaveButton:
        return re.sub(r"\n<!--\/?HAS_SAVE_BTN-->", '', tpl)
    else:
        return re.sub(r"\n<!--HAS_SAVE_BTN-->((?!<!--\/HAS_SAVE_BTN-->).)*\n<!--\/HAS_SAVE_BTN-->", '', tpl, flags=re.DOTALL)

components = []
routes = []
settingsItems = []

for compParams in COMPONENTS_LIST:
    compName = compParams[0]
    hasSaveButton = compParams[3] != None
    compNameCamel = camelize(compName) + 'SettingsComponent'
    compHtmlClassName = compName + '-editor'

    placeholders = {
        'component-dash-name': compName,
        'component-name': compNameCamel,
        'component-html-class-name': compHtmlClassName,
        'component-page-title': compParams[1],
        'component-page-header': compParams[2],
        'component-save-button': compParams[3],
        'settings-item-caption': compParams[4],
        'settings-item-feature': compParams[5]
    }

    components.append(compNameCamel + ',')
    settingsItems.append(fillPlaceholders(COMPONENT_SETTINGS_ITEM_TPL, placeholders))
    routes.append(fillPlaceholders(COMPONENT_ROUTE_TPL, placeholders))
    files = {
        'ts': replceSaveButton(fillPlaceholders(COMPONENT_SRC_TPL, placeholders), hasSaveButton),
        'html': replceSaveButton(fillPlaceholders(COMPONENT_HTML_TPL, placeholders), hasSaveButton),
        'scss': fillPlaceholders(COMPONENT_SCSS_TPL, placeholders)
    }

    compDir = './' + compName

    if not os.path.exists(compDir):
        os.mkdir(compDir)

    for ext, content in files.items():
        with open('{}/{}.component.{}'.format(compDir, compName, ext), 'w', encoding='utf-8') as f:
            f.write(content)

print('\n'.join(components), '\n\n')
print('\n'.join(settingsItems), '\n\n')
print('\n'.join(routes), '\n\n')
