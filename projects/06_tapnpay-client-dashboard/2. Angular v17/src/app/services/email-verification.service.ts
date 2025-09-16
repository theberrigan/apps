import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpService } from './http.service';

@Injectable({ providedIn: 'root' })
export class EmailVerificationService {
  constructor(private http: HttpService) {}

  confirmVerifyEmail(token: string): Observable<any> {
    return this.http.post('endpoint://email.verify', {
      urlParams: { token }
    });
  }
} 