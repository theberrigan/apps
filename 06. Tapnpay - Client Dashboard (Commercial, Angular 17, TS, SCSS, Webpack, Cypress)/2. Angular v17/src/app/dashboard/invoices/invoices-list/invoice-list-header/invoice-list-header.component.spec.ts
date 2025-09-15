import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvoiceListHeaderComponent } from './invoice-list-header.component';

describe('InvoiceListHeaderComponent', () => {
  let component: InvoiceListHeaderComponent;
  let fixture: ComponentFixture<InvoiceListHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InvoiceListHeaderComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InvoiceListHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
