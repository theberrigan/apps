import { TestBed } from '@angular/core/testing';

import { AutopaymentService } from './autopayment.service';

describe('AutopaymentService', () => {
  let service: AutopaymentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AutopaymentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
