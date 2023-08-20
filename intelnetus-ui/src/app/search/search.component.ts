import { Component, ViewChildren, QueryList, ViewChild, AfterViewInit } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { NgForm } from "@angular/forms";
import { SearchService } from "./search-service/search.service";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})

export class SearchComponent {
  @ViewChildren('dynamicInputs') dynamicInputs!: QueryList<any>;
  public successful: any = null;
  public hasResults: any = null;
  public keywordSets: any[] = [];
  public data = <any>[];
  public variants = <any>[];
  public dataLoaded = false;
  public duplicatesFlag: boolean;
  public enableScopusSearch: boolean = true;
  public year1: string;
  public year2: string;
  public scopusApiKey:string;
  public keywords = <any>[];
  public booleans = <any>[];
  public fields = <any>[];
  public booleanOptions = ['AND','OR','AND NOT'];
  public options = [
    { id: "0", name: "Agricultural and Biological Sciences", selected: false },
    { id: "1", name: "Arts and Humanities", selected: false },
    { id: "2", name: "Biochemistry Genetics and Molecular Biology", selected: false },
    { id: "3", name: "Business, Management, and Accounting", selected: false },
    { id: "4", name: "Chemical Engineering", selected: false },
    { id: "5", name: "Chemistry", selected: false },
    { id: "6", name: "Computer Science", selected: false },
    { id: "7", name: "Decision Sciences", selected: false },
    { id: "8", name: "Dentistry", selected: false },
    { id: "9", name: "Earth and Planetary Sciences", selected: false },
    { id: "10", name: "Economics, Econometrics and Finance", selected: false },
    { id: "11", name: "Energy", selected: false },
    { id: "12", name: "Engineering", selected: false },
    { id: "13", name: "Environmental Science", selected: false },
    { id: "14", name: "Health Professions", selected: false },
    { id: "15", name: "Immunology and Microbiology", selected: false },
    { id: "16", name: "Materials Science", selected: false },
    { id: "17", name: "Mathematics", selected: false },
    { id: "18", name: "Medicine", selected: false },
    { id: "19", name: "Multidisciplinary", selected: false },
    { id: "20", name: "Neuroscience", selected: false },
    { id: "21", name: "Nursing", selected: false },
    { id: "22", name: "Pharmacology, Toxicology, and Pharmaceutics", selected: false },
    { id: "23", name: "Physics and Astronomy", selected: false },
    { id: "24", name: "Psychology", selected: false },
    { id: "25", name: "Social Sciences", selected: false },
    { id: "26", name: "Veterinary", selected: false }
  ]

  constructor(
    private http: HttpClient,
    private _searchSrvc: SearchService
  ) { }

  ngOnInit() { }

  removeSet(i: any) {
    this.keywordSets.splice(i, 1);
  }

  addSet() {
    const keyword = { value: '' };
    this.keywordSets.push(keyword);
  }

  setScopusSearch() {
    this.enableScopusSearch = !this.enableScopusSearch;
  }

  onSubmit(form: NgForm) {
    let formData = form.value;
    Object.keys(formData).forEach(key => {
      if (key.includes('keyword')) {
        this.keywords.push(formData[key]);
      }
      else if (key.includes('boolean')) {
        this.booleans.push(formData[key]);
      }
      else if (key.includes('year1')) {
        this.year1 = formData[key];
      }
      else if (key.includes('year2')) {
        this.year2 = formData[key];
      }
      else if (key.includes('scopus')) {
        this.scopusApiKey = formData[key];
      }
      else if (formData[key] == true) {
        this.fields.push(this.options.find(field => field.name === key)?.id)
      }
    });

    this._searchSrvc.getMetadata(this.keywords, this.booleans, this.year1, this.year2, this.fields, this.scopusApiKey)
      .subscribe((response: any) => {
        if (response.successful === "false") {
          this.successful = false;
          this.hasResults = false;
        }
        else if (response.successful === "true" && response.hasResult === "false") {
          this.successful = true;
          this.hasResults = false;
        }
        else {
          this.successful = true;
          this.hasResults = true;
          this.data = response.data;
          this.variants = response.variants;

          if (this.variants.publicationsVariants.duplicates.length > 0 || 
            this.variants.authorsVariants.duplicates.length > 0 || 
            this.variants.organizationsVariants.duplicates.length > 0) {
            this.duplicatesFlag = true;
          }
          else {
            this.duplicatesFlag = false;
          }
        }
      });

    form.resetForm();
    this.keywords = [];
    this.booleans = [];
    this.fields = [];
    this.dynamicInputs.forEach(input => this.removeSet(input));
    this.dataLoaded = true;
  }

  onReset(reset: boolean) {
    this.dataLoaded = !reset;
    this.successful = null;
    this.hasResults = null;
  }

}