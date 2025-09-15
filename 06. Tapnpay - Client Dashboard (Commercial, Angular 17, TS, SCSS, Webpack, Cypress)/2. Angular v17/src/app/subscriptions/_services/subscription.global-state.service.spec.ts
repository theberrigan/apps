import { TestBed } from '@angular/core/testing';

import { FlowGlobalStateService } from './flow-global-state.service';

describe('SubscriptionGlobalStateService', () => {
  let service: FlowGlobalStateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FlowGlobalStateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
