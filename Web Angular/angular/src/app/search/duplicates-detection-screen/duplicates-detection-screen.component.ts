import { Component, Inject } from '@angular/core';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-duplicates-detection-screen',
  templateUrl: './duplicates-detection-screen.component.html',
  styleUrls: ['./duplicates-detection-screen.component.css']
})
export class DuplicatesDetectionScreenComponent {

  constructor(
    public dialogRef: MatDialogRef<DuplicatesDetectionScreenComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  close() {
    this.dialogRef.close();
  }
}
