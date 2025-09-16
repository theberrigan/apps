import { TestBed } from '@angular/core/testing';

import { IsShowAddVehicleModalAfterLoginService } from './is-show-add-vehicle-modal-after-login.service';

describe('IsShowAddVehicleModalAfterLoginService', () => {
  let service: IsShowAddVehicleModalAfterLoginService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(IsShowAddVehicleModalAfterLoginService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
