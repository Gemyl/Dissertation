import { Component, ViewChild, Input, Output, AfterViewInit, EventEmitter } from '@angular/core';
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
import { MatTooltipModule } from '@angular/material/tooltip';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-metadata-table',
  templateUrl: './metadata-table.component.html',
  styleUrls: ['./metadata-table.component.scss']
})
export class MetadataTableComponent implements AfterViewInit {
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @Output() reset: EventEmitter<boolean> = new EventEmitter<boolean>();
  @Input() set tableData(data:any) {
    this.length = data.length;
      this.dataSource = new MatTableDataSource(data);
      this.dataSource.data = data;
      this.dataSource.paginator = this.paginator;
  };
  public dataSource: any;
  displayedColumns: string[] = [
    'DOI', 'Year', 'Citations Count', 'Keywords', 'Scientific Fields',
    'Author First Name', 'Author Last Name', 'Fields Of Study', 'Author Citations Count',
    'Organization Name', 'Type 1 (Primary)', 'Type 2 (Secondary)', 'City', 'Country'
  ];
  length: number;
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [5, 10];
  headers = {
    publicationDoi:"DOI",
    publicationYear:"Year",
    publicationCitationsCount:"Citations Count",
    publicationKeywords:"Keywords",
    publicationFields:"Fields",
    authorFirstName:"Author First Name",
    authorLastName:"Author Last Name",
    authorFieldsOfStudy:"Fields Of Study",
    authorCitationsCount:"Author Citations Count",
    organizationName:"Organization Name",
    organizationType1:"Type 1 (Primary)",
    organizationType2:"Type 2 (Secondary)",
    organizationCity:"City",
    organizationCountry:"Country"
  }

  ngOnInit() {
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
  }

  newSearch() {
    this.reset.emit(true);
  }

  exportToExcel(): void {
    var data = this.dataSource.data;

    let file = this.sortExportFileData(data);

    /* create a new workbook and worksheet */
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.aoa_to_sheet(file);
  
    /* add the worksheet to the workbook */
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  
    /* generate the file and download it */
    XLSX.writeFile(workbook, 'table-data.xlsx');
  }

  exportToCsv() {
    let fileContent = this.sortExportFileData(this.dataSource.data);
    const csvData = this.convertToCsv(fileContent, ',');
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'Metadata.csv');
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
  
}
