import { Component, ViewChild, Input, Output, AfterViewInit, EventEmitter } from '@angular/core';
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
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
  displayedColumns: string[] = ['doi', 'citations'];
  length: number;
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [5, 10, 25, 50 , 100];

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
    let headers = []
    let cells = []
    let file = []

    for (let i = 0; i < data.length; i++) {
      cells = []
      if (i === 0) {
        for (let key in data[i]) {
          headers.push(key)
        }
        headers.reverse();
        file.push(headers)
      }
      for (let key in data[i]) {
        cells.push(data[i][key])
      }
      cells.reverse();
      file.push(cells.slice()) // create a new array for each row
    }

    /* create a new workbook and worksheet */
    const workbook = XLSX.utils.book_new();
    const worksheet = XLSX.utils.aoa_to_sheet(file);
  
    /* add the worksheet to the workbook */
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  
    /* generate the file and download it */
    XLSX.writeFile(workbook, 'table-data.xlsx');
  }

  exportToCsv() {
    const csvData = this.convertToCsv(this.dataSource.data, ',');
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, 'Metadata.csv');
  }

  convertToCsv(data: any[], delimeter: string) {
    const header = Object.keys(data[0]).join(delimeter);
    const rows = data.map(obj => Object.values(obj).join(delimeter));
    return `${header}\n${rows.join('\n')}`;
  }
}
