import {Injectable} from '@angular/core';
import {Router} from "@angular/router";

@Injectable({
    providedIn: 'root'
})
export class IsShowAddVehicleModalAfterLoginService {

    constructor(private router: Router) {
    }


    isShow() {
        return sessionStorage.getItem('showAddVehicleModal') && sessionStorage.getItem('showAddVehicleModal') === 'true';
    }

    setToShow() {
        if (!sessionStorage.getItem('showAddVehicleModal')) {
            sessionStorage.setItem('showAddVehicleModal', 'true');
        }
    }

    show() {
        this.router.navigate(
            ['/dashboard/profile/vehicles']
        );
    }

    checkAndShow() {
        if (this.isShow()) {
            this.show();
        }
    }

    hide() {
        if (sessionStorage.getItem('showAddVehicleModal')) {
            sessionStorage.setItem('showAddVehicleModal', 'false');
        }
    }

    deleteOption() {
        sessionStorage.removeItem('showAddVehicleModal');
    }
}
