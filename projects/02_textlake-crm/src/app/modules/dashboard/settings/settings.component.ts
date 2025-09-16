import {Component, ViewEncapsulation} from '@angular/core';
import {Subscription} from 'rxjs';
import {Router} from '@angular/router';
import {UserData, UserFeatures, UserService} from '../../../services/user.service';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'settings',
    templateUrl: './settings.component.html',
    styleUrls: [ './settings.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'settings',
    }
})
export class SettingsComponent {
    public subs : Subscription[] = [];

    public features : UserFeatures;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
    ) {
        this.titleService.setTitle('settings.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.features = userData.features;
    }

    public isItemVisible (featureKey : string) : boolean {
        return this.features && this.features.can(featureKey);
    }
}
