import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { NavService } from '../services/nav.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-nav-mobile-logout-confirm',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './nav-mobile-logout-confirm.component.html',
  styleUrl: './nav-mobile-logout-confirm.component.css'
})
export class NavMobileLogoutConfirmComponent {
  constructor(
    private router: Router,
    private userService: UserService,
    private navService: NavService
  ) {}

  onNo() {
    this.router.navigateByUrl('/dashboard/invoices');
    this.navService.navMessagePipe.next({ action: 'hide' });
  }

  onYes() {
    this.userService.logout();
    this.router.navigateByUrl('/auth');
    this.navService.navMessagePipe.next({ action: 'hide' });
  }
}
