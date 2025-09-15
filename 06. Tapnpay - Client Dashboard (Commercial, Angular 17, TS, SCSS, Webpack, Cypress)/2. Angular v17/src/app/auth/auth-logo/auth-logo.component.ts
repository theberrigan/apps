import {Component, OnInit} from '@angular/core';
import { NEO_RIDE_LOGO_URL } from '../../constants/logo.constants';

@Component({
    selector: 'app-auth-logo',
    templateUrl: './auth-logo.component.html',
    styleUrls: ['./auth-logo.component.css']
})
export class AuthLogoComponent implements OnInit {

    public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;

    constructor() {
    }

    ngOnInit(): void {
    }

}
