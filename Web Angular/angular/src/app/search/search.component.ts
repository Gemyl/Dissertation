import { Component, ViewChildren, QueryList, ViewChild, AfterViewInit } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { NgForm } from "@angular/forms";
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements AfterViewInit {
  @ViewChildren('dynamicInputs') dynamicInputs!: QueryList<any>;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  public keywordSets: any[] = [];
  public data = <any>[];
  public dataLoaded = false;
  dataSource = new MatTableDataSource();
  displayedColumns: string[] = ['doi', 'citations'];
  length!: number;
  pageSize = 10;
  pageIndex = 0;
  pageSizeOptions = [5, 10, 25, 50 , 100];
  options = [
    {name:"Agricultural and Biological Sciences", selected: false},
    {name:"Arts and Humanities", selected: false},
    {name:"Biochemistry Genetics and Molecular Biology", selected: false},
    {name:"Business, Management, and Accounting", selected: false},
    {name:"Chemical Engineering", selected: false},
    {name:"Chemistry", selected: false},
    {name:"Computer Science", selected: false},
    {name:"Decision Sciences", selected: false},
    {name:"Dentistry", selected: false},
    {name:"Earth and Planetary Sciences", selected: false},
    {name:"Economics, Econometrics and Finance", selected: false},
    {name:"Energy", selected: false},
    {name:"Engineering", selected: false},
    {name:"Environmental Science", selected: false},
    {name:"Health Professions", selected: false},
    {name:"Immunology and Microbiology", selected: false},
    {name:"Materials Science", selected: false},
    {name:"Mathematics", selected: false},
    {name:"Medicine", selected: false},
    {name:"Multidisciplinary", selected: false},
    {name:"Neuroscience", selected: false},
    {name:"Nursing", selected: false},
    {name:"Pharmacology, Toxicology, and Pharmaceutics", selected: false},
    {name:"Physics and Astronomy", selected: false},
    {name:"Psychology", selected: false},
    {name:"Social Sciences", selected: false},
    {name:"Veterinary", selected: false}    
  ]

  constructor(
    private http: HttpClient
  ){}

  ngOnInit() {}
  
  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
  }

  removeSet(i:any){
    this.keywordSets.splice(i,1);
  }

  addSet(){
    const keyword = {value: '' };
    this.keywordSets.push(keyword);
  }

  onSubmit(form: NgForm) {
    this.http
      .get("http://127.0.0.1:5000/search", { params: form.value })
      .subscribe(response => {
        this.data = response;
        this.dataSource.data = this.data;
      });
    this.length = this.data.length;
    this.dataLoaded = true;
    form.resetForm();
    this.dynamicInputs.forEach(input => this.removeSet(input));
  }

  exportAsExcel(): void {
    /* get the table data from the component */
    let headers = []
    let cells = []
    let file = []

    for (let i = 0; i < this.data.length; i++) {
      cells = [] // clear cells array for each row
      if (i === 0) {
        for (let key in this.data[i]) {
          headers.push(key)
        }
        headers.reverse();
        file.push(headers)
      }
      for (let key in this.data[i]) {
        cells.push(this.data[i][key])
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
  
}