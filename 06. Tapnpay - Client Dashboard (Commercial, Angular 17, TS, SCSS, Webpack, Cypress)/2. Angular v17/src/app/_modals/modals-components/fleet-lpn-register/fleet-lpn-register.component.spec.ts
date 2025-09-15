import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FleetLpnRegisterComponent } from './fleet-lpn-register.component';

describe('FleetLpnRegisterComponent', () => {
  let component: FleetLpnRegisterComponent;
  let fixture: ComponentFixture<FleetLpnRegisterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FleetLpnRegisterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FleetLpnRegisterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
