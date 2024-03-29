import { Component, ViewChild, Input, Output, EventEmitter } from '@angular/core';
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSortModule, MatSort, Sort } from '@angular/material/sort';
import { MatFormField } from '@angular/material/form-field';
import { MatLabel } from '@angular/material/form-field';
import { MatDrawer } from '@angular/material/sidenav';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DuplicatesDetectionScreenComponent } from '../duplicates-detection-screen/duplicates-detection-screen.component';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { SearchService } from '../search-service/search.service';

@Component({
  selector: 'app-metadata-table',
  templateUrl: './metadata-table.component.html',
  styleUrls: ['./metadata-table.component.scss']
})
export class MetadataTableComponent {
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sorting: MatSort;
  @Output() reset: EventEmitter<boolean> = new EventEmitter<boolean>();
  @Input() variants: any;
  @Input() hasDuplicates: boolean;
  @Input() successful: boolean;
  @Input() hasResults: boolean;
  @Input() set tableData(data: any) {
    if (this.renderSpinner) {
      this.renderTable = true;
      this.renderSpinner = false;
      setTimeout(() => {
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sorting;
      });
      this.dataSource = new MatTableDataSource(data);
      this.dataSource.data = data;
      this.length = this.dataSource.data.length;
    }
  }
  public dataSource: any;
  public renderSpinner: boolean;
  public renderTable: boolean;
  displayedColumns: string[] = [
    'publicationDoi', 'publicationTitle', 'publicationYear', 'publicationCitationsCount', 'publicationKeywords', 'publicationFields',
    'authorFirstName', 'authorLastName', 'authorFieldsOfStudy', 'authorCitationsCount', 'authorhIndex',
    'organizationName', 'organizationType1', 'organizationType2', 'organizationCity', 'organizationCountry'
  ];
  showFiller = false;
  length: number;
  pageSize = 10;
  pageIndex = 0;
  headers = {
    publicationDoi: "DOI",
    publicationTitle: "Title",
    publicationYear: "Year",
    publicationCitationsCount: "Citations Count",
    publicationKeywords: "Keywords",
    publicationFields: "Fields",
    authorFirstName: "Author First Name",
    authorLastName: "Author Last Name",
    authorFieldsOfStudy: "Fields Of Study",
    authorCitationsCount: "Author Citations Count",
    organizationName: "Organization Name",
    organizationType1: "Type 1 (Primary)",
    organizationType2: "Type 2 (Secondary)",
    organizationCity: "City",
    organizationCountry: "Country"
  }

  constructor(
    public dialog: MatDialog,
    public _searchService: SearchService
  ) { }

  openDialog() {
    const dialogRef = this.dialog.open(DuplicatesDetectionScreenComponent ,{
      data: [this.dataSource.data, this.variants]
    })

    dialogRef.afterClosed().subscribe((result:any) => {
      this.hasDuplicates = result;
    });
  }
  
  ngOnInit() {
    this._searchService.getTableData().subscribe(data => {
      if (this.dataSource && data.length > 0) {
        this.dataSource.data = data;
        this.length = data.length;
      }
    });
    this.renderSpinner = true;
  }

  changeFiller() {
    if (this.showFiller) {
      this.showFiller = false;
    }
    else {
      this.showFiller = true;
    }
  }

  newSearch() {
    this.reset.emit(true);
  }

  exportToExcel(): void {
    var data = this.dataSource.filteredData;
    let file = this.sortExportFileData(data);
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.aoa_to_sheet(file);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
    XLSX.writeFile(workbook, 'IntelnetusMetadata.xlsx');
  }

  exportToCsv() {
    let fileContent = this.sortExportFileData(this.dataSource.filteredData);
    const csvData = this.convertToCsv(fileContent, ',');
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'IntelnetusMetadata.csv');
  }

  convertToCsv(data: any[], delimeter: string) {
    const header = Object.keys(data[0]).join(delimeter);
    const rows = data.map(obj => Object.values(obj).join(delimeter));
    return `${header}\n${rows.join('\n')}`;
  }

  sortExportFileData(data: any[]) {
    let headers = Object.values(this.headers);
    let fileContent = [headers];

    for (let i = 0; i < data.length; i++) {
      let row = [];
      for (let headersKey in this.headers) {
        if (Object.prototype.hasOwnProperty.call(this.headers, headersKey)) {
          let dataKey = headersKey;
          row.push(data[i][dataKey]);
        }
      }
      fileContent.push(row.slice());
    }
    return fileContent;
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    console.log(this.dataSource.sortData)
  }
}
