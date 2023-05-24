import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SearchService } from '../search-service/search.service';
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-duplicates-detection-screen',
  templateUrl: './duplicates-detection-screen.component.html',
  styleUrls: ['./duplicates-detection-screen.component.css']
})
export class DuplicatesDetectionScreenComponent implements OnInit {
  public publicationsVariantsNumber: number;
  public authorsVariantsNumber: number;
  public organizationsVariantsNumber: number;
  public publicationsOption: boolean;
  public authorsOption: boolean;
  public organizationsOption: boolean;
  public originalPublications: any;
  public duplicatesPublications: any;
  public publicationsTableColumns = ["title", "citationsCount", "checkbox"]
  public publicationsToRemove: string[] = [];

  constructor(
    public dialogRef: MatDialogRef<DuplicatesDetectionScreenComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private _searchService: SearchService
  ) { 
    this.originalPublications = new MatTableDataSource(this.data[1].publicationsVariants.originals);
    this.duplicatesPublications = new MatTableDataSource(this.data[1].publicationsVariants.duplicates);
    this.originalPublications.data = this.data[1].publicationsVariants.originals;
    this.duplicatesPublications.data = this.data[1].publicationsVariants.duplicates;
  }

  ngOnInit(): void {
    this.publicationsVariantsNumber = this.data[1].publicationsVariants.duplicates.length;
    this.authorsVariantsNumber = this.data[1].authorsVariants.duplicates.length;
    this.organizationsVariantsNumber = this.data[1].organizationsVariants.duplicates.length;
  }

  close() {
    this.dialogRef.close();
  }

  // clearDuplicates() {
  //   let referenceValue = this.data[1].publicationsVariants.originals[0].id;
  //   let filteredData = this.data[0].filter((d:any) => d.publicationId === referenceValue);
  //   this._searchService.setTableData(filteredData);
  // }

  selectMode(option:string) {
    if (option === "publications") {
      this.publicationsOption = true;
      this.authorsOption = false;
      this.organizationsOption = false;
    }
    else if (option === "authors") {
      this.publicationsOption = false;
      this.authorsOption = true;
      this.organizationsOption = false;
    }
    else if (option === "organizations") {
      this.publicationsOption = false;
      this.authorsOption = false;
      this.organizationsOption = true;
    }
  }

  changePublicationsVariantsList(publicationId:string) {
    debugger;
    let index = this.publicationsToRemove.indexOf(publicationId);
    if (index > 0) {
      this.publicationsToRemove.splice(index,1);
    }
    else {
      this.publicationsToRemove.push(publicationId);
    }
  }

  clearDuplicates() {
    debugger;
    let filteredData = this.data[0];
    for(let i = 0; i < this.publicationsToRemove.length; i++) {
      filteredData = filteredData.filter((x:any) => x.publicationId != this.publicationsToRemove[i]); 
    }
    this._searchService.setTableData(filteredData);
  }
}
