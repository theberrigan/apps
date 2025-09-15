import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InvoiceListItemComponent } from './invoice-list-item.component';

describe('InvoiceListItemComponent', () => {
  let component: InvoiceListItemComponent;
  let fixture: ComponentFixture<InvoiceListItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InvoiceListItemComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InvoiceListItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
