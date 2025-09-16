import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { EmailVerificationService } from '../services/email-verification.service';
import { HttpErrorResponse } from '@angular/common/http';
import { NEO_RIDE_LOGO_URL } from '../constants/logo.constants';

@Component({
  selector: 'app-email-verification',
  templateUrl: './email-verification.component.html',
  styleUrls: ['./email-verification.component.scss']
})
export class EmailVerificationComponent implements OnInit {
  status: 'loading' | 'success' | 'already' | 'expired' | 'error' = 'loading';
  public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;

  constructor(
    private route: ActivatedRoute,
    private emailVerificationService: EmailVerificationService
  ) {}

  ngOnInit() {
    const token = this.route.snapshot.paramMap.get('token');
    if (token) {
      this.emailVerificationService.confirmVerifyEmail(token).subscribe({
        next: (res) => {
          if (res.status === 'Success') {
            this.status = 'success';
          } else if (res.status === 'EmailAlreadyVerified') {
            this.status = 'already';
          } else if (res.status === 'TokenNotExistsOrExpired') {
            this.status = 'expired';
          } else {
            this.status = 'error';
          }
        },
        error: (err: HttpErrorResponse) => {
          if (err.status === 409) {
            this.status = 'already';
          } else if (err.status === 410) {
            this.status = 'expired';
          } else {
            this.status = 'error';
          }
        }
      });
    } else {
      this.status = 'error';
    }
  }
} 