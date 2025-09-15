import { TestBed } from '@angular/core/testing';

import { ConfirmFleetPaymentService } from './confirm-fleet-payment.service';

describe('ConfirmFleetPaymentService', () => {
  let service: ConfirmFleetPaymentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConfirmFleetPaymentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
