import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DuplicatesDetectionScreenComponent } from './duplicates-detection-screen.component';

describe('DuplicatesDetectionScreenComponent', () => {
  let component: DuplicatesDetectionScreenComponent;
  let fixture: ComponentFixture<DuplicatesDetectionScreenComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DuplicatesDetectionScreenComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DuplicatesDetectionScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
