import { Component, ViewChildren, QueryList, ViewChild, AfterViewInit } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { NgForm } from "@angular/forms";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent {
  @ViewChildren('dynamicInputs') dynamicInputs!: QueryList<any>;
  public keywordSets: any[] = [];
  public data = <any>[];
  public dataLoaded = false;
  options = [
    { name: "Agricultural and Biological Sciences", selected: false },
    { name: "Arts and Humanities", selected: false },
    { name: "Biochemistry Genetics and Molecular Biology", selected: false },
    { name: "Business, Management, and Accounting", selected: false },
    { name: "Chemical Engineering", selected: false },
    { name: "Chemistry", selected: false },
    { name: "Computer Science", selected: false },
    { name: "Decision Sciences", selected: false },
    { name: "Dentistry", selected: false },
    { name: "Earth and Planetary Sciences", selected: false },
    { name: "Economics, Econometrics and Finance", selected: false },
    { name: "Energy", selected: false },
    { name: "Engineering", selected: false },
    { name: "Environmental Science", selected: false },
    { name: "Health Professions", selected: false },
    { name: "Immunology and Microbiology", selected: false },
    { name: "Materials Science", selected: false },
    { name: "Mathematics", selected: false },
    { name: "Medicine", selected: false },
    { name: "Multidisciplinary", selected: false },
    { name: "Neuroscience", selected: false },
    { name: "Nursing", selected: false },
    { name: "Pharmacology, Toxicology, and Pharmaceutics", selected: false },
    { name: "Physics and Astronomy", selected: false },
    { name: "Psychology", selected: false },
    { name: "Social Sciences", selected: false },
    { name: "Veterinary", selected: false }
  ]

  constructor(
    private http: HttpClient
  ) { }

  ngOnInit() { }

  removeSet(i: any) {
    this.keywordSets.splice(i, 1);
  }

  addSet() {
    const keyword = { value: '' };
    this.keywordSets.push(keyword);
  }

  onSubmit(form: NgForm) {
    this.http
      .get("http://127.0.0.1:5000/search", { params: form.value })
      .subscribe(response => {
        this.data = response;
      });
    this.dataLoaded = true;
    form.resetForm();
    this.dynamicInputs.forEach(input => this.removeSet(input));
  }

  onReset(reset: boolean) {
    this.dataLoaded = !reset;
  }

}