import { TestBed } from '@angular/core/testing';

import { UserMainInfoService } from './user-main-info.service';

describe('UserMainInfoService', () => {
  let service: UserMainInfoService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UserMainInfoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
