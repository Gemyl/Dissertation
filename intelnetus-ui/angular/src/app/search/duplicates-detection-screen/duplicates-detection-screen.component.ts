import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { SearchService } from '../search-service/search.service';
import { MatTableDataSource } from "@angular/material/table";
import { MatPaginator } from "@angular/material/paginator";
import { MatTooltipModule } from '@angular/material/tooltip';
import { CheckBoxModule } from '@progress/kendo-angular-treeview/checkbox/checkbox.module';

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
  public primaryPublications: any;
  public primaryAuthors: any;
  public primaryOrganizations: any;
  public secondaryPublications: any;
  public secondaryAuthors: any;
  public secondaryOrganizations: any;
  public publicationsTableColumns = ["title", "citationsCount", "checkbox"]
  public authorsTableColumns = ["name", "citationsCount", "hIndex", "checkbox"]
  public organizationsTableColumns = ["name", "checkbox"]
  public publicationsToBeRemoved: string[] = [];
  public authorsToBeReplaced: string[] = [];
  public authorsToReplace: string[] = [];
  public organizationsToBeReplaced: string[] = [];
  public organizationsToReplace: string[] = [];
  public dialogResult: boolean = true;
  public primaryPublicationsSelected: boolean = false;
  public secondaryPublicationsSelected: boolean = false;
  public primaryAuthorsSelected: boolean = false;
  public secondaryAuthorsSelected: boolean = false;
  public primaryOrganizationsSelected: boolean = false;
  public secondaryOrganizationsSelected: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<DuplicatesDetectionScreenComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private _searchService: SearchService
  ) { 
    this.primaryPublications = new MatTableDataSource(this.data[1].publicationsVariants.originals);
    this.secondaryPublications = new MatTableDataSource(this.data[1].publicationsVariants.duplicates);
    this.primaryPublications.data = this.data[1].publicationsVariants.originals;
    this.secondaryPublications.data = this.data[1].publicationsVariants.duplicates;

    this.primaryAuthors = new MatTableDataSource(this.data[1].authorsVariants.originals);
    this.secondaryAuthors = new MatTableDataSource(this.data[1].authorsVariants.duplicates);
    this.primaryAuthors.data = this.data[1].authorsVariants.originals;
    this.secondaryAuthors.data = this.data[1].authorsVariants.duplicates;

    this.primaryOrganizations = new MatTableDataSource(this.data[1].organizationsVariants.originals);
    this.secondaryOrganizations = new MatTableDataSource(this.data[1].organizationsVariants.duplicates);
    this.primaryOrganizations.data = this.data[1].organizationsVariants.originals;
    this.secondaryOrganizations.data = this.data[1].organizationsVariants.duplicates;
  }

  ngOnInit(): void {
    this.publicationsVariantsNumber = this.data[1].publicationsVariants.duplicates.length;
    this.authorsVariantsNumber = this.data[1].authorsVariants.duplicates.length;
    this.organizationsVariantsNumber = this.data[1].organizationsVariants.duplicates.length;
  }

  onClose() {
    if (this.data[1].publicationsVariants.duplicates.length === 0 && 
        this.data[1].authorsVariants.duplicates.length === 0 &&
        this.data[1].organizationsVariants.duplicates.length === 0) {
          this.dialogResult = false;
    }
    this.dialogRef.close(this.dialogResult);
  }

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
    else {
      this.publicationsOption = false;
      this.authorsOption = false;
      this.organizationsOption = false;
    }
  }

  selectColumn(entityType:string, isEntityPrimary:boolean) {
    if (entityType === "publication") {
      if (isEntityPrimary) {
        if (this.primaryPublicationsSelected) {
          this.primaryPublicationsSelected = false;
          this.publicationsToBeRemoved = [];
        }
        else {
          this.primaryPublicationsSelected = true;
          for (let i = 0; i < this.primaryPublications.data.length; i++) {
            this.updatePublicationsVariantsList(this.primaryPublications.data[i].id, true);
          }
        }
      }
      else {
        if (this.secondaryPublicationsSelected) {
          this.secondaryPublicationsSelected = false;
          this.publicationsToBeRemoved = [];
        }
        else {
          this.secondaryPublicationsSelected = true;
          for (let i = 0; i < this.secondaryPublications.data.length; i++) {
            this.updatePublicationsVariantsList(this.secondaryPublications.data[i].id, true);
          }
        }
      }
    }

    else if (entityType === "author") {
      if (isEntityPrimary) {
        if (this.primaryAuthorsSelected) {
          this.primaryAuthorsSelected = false;
          this.authorsToBeReplaced = [];
        }
        else {
          this.primaryAuthorsSelected = true;
          for (let i = 0; i < this.primaryAuthors.data.length; i++) {
            this.updateAuthorsVariantsList(this.primaryAuthors.data[i], true);
          }
        }
      }
      else {
        if (this.secondaryAuthorsSelected) {
          this.secondaryAuthorsSelected = false;
          this.authorsToBeReplaced = [];
        }
        else {
          this.secondaryAuthorsSelected = true;
          for (let i = 0; i < this.secondaryAuthors.data.length; i++) {
            this.updateAuthorsVariantsList(this.secondaryAuthors.data[i], true);
          }
        }
      }
    }

    else if (entityType === "organization") {
      if (isEntityPrimary) {
        if (this.primaryOrganizationsSelected) {
          this.primaryOrganizationsSelected = false;
          this.organizationsToBeReplaced = [];
        }
        else {
          this.primaryOrganizationsSelected = true;
          for (let i = 0; i < this.primaryOrganizations.data.length; i++) {
            this.updateOrganizationsVariantsList(this.primaryOrganizations.data[i], true);
          }
        }
      }
      else {
        if (this.secondaryOrganizationsSelected) {
          this.secondaryOrganizationsSelected = false;
          this.organizationsToBeReplaced = [];
        }
        else {
          this.secondaryOrganizationsSelected = true;
          for (let i = 0; i < this.secondaryOrganizations.data.length; i++) {
            this.updateOrganizationsVariantsList(this.secondaryOrganizations.data[i], true);
          }
        }
      }
    }
  }

  updatePublicationsVariantsList(publicationId:string, allowDuplicates:boolean = false) {
    let index = this.publicationsToBeRemoved.indexOf(publicationId);
    if (index >= 0 && !allowDuplicates) {
      this.publicationsToBeRemoved.splice(index,1);
    }
    else {
      this.publicationsToBeRemoved.push(publicationId);
    }
  }

  clearPublicationsDuplicates() {
    let filteredData = this.data[0];

    for(let i = 0; i < this.publicationsToBeRemoved.length; i++) {
      filteredData = filteredData.filter((x:any) => x.publicationId !== this.publicationsToBeRemoved[i]); 
    }

    for (let i = 0; i < this.publicationsToBeRemoved.length; i++) {
      let index = this.primaryPublications.data.indexOf(this.primaryPublications.data.find((x:any) => x.id === this.publicationsToBeRemoved[i])) > -1
        ? this.primaryPublications.data.indexOf(this.primaryPublications.data.find((x:any) => x.id === this.publicationsToBeRemoved[i]))
        : this.secondaryPublications.data.indexOf(this.secondaryPublications.data.find((x:any) => x.id === this.publicationsToBeRemoved[i]));

      this.primaryPublications.data.splice(index,1);
      this.secondaryPublications.data.splice(index,1);
    }

    this._searchService.setTableData(filteredData);
    this.publicationsVariantsNumber = this.data[1].publicationsVariants.duplicates.length;
    this.publicationsToBeRemoved = [];
    this.selectMode('reset');
  }

  updateAuthorsVariantsList(author:any, allowDuplicates:boolean = false) {
    let index = this.authorsToBeReplaced.indexOf(author.id);
    if (index >= 0 && !allowDuplicates) {
      this.authorsToBeReplaced.splice(index,1);
      this.authorsToReplace.splice(index,1);
    }
    else {
      index = this.primaryAuthors.data.indexOf(author);
      if (index >= 0) {
        this.authorsToReplace.push(this.secondaryAuthors.data[index].id);
      }
      else {
        index = this.secondaryAuthors.data.indexOf(author);
        this.authorsToReplace.push(this.primaryAuthors.data[index].id);
      }
      this.authorsToBeReplaced.push(author.id);
    }
  }

  clearAuthorsDuplicates() {
    let filteredData = this.data[0];
    let replacingAuthorsObjects = this.authorsToReplace.map((authorId:string) => filteredData.find((object:any) => object.authorId === authorId));

    for (let i = 0; i < filteredData.length; i++) {
      let index = this.authorsToBeReplaced.indexOf(filteredData[i].authorId);
      if (index >= 0) {
        filteredData[i].authorId = replacingAuthorsObjects[index].authorId;
        filteredData[i].authorFirstName = replacingAuthorsObjects[index].authorFirstName;
        filteredData[i].authorLastName = replacingAuthorsObjects[index].authorLastName;
        filteredData[i].authorFieldsOfStudy = replacingAuthorsObjects[index].authorFieldsOfStudy;
        filteredData[i].authorCitationsCount = replacingAuthorsObjects[index].authorCitationsCount;
        filteredData[i].authorhIndex = replacingAuthorsObjects[index].authorhIndex;
      }
    }

    this._searchService.setTableData(filteredData);
    for (let i = 0; i < this.authorsToBeReplaced.length; i++) {
      let index = this.primaryAuthors.data.indexOf(this.primaryAuthors.data.find((x:any) => x.id === this.authorsToBeReplaced)) > -1
        ? this.primaryAuthors.data.indexOf(this.primaryAuthors.data.find((x:any) => x.id === this.authorsToBeReplaced))
        : this.secondaryAuthors.data.indexOf(this.secondaryAuthors.data.find((x:any) => x.id === this.authorsToBeReplaced))
      
      this.primaryAuthors.data.splice(index,1);
      this.secondaryAuthors.data.splice(index,1);
    }

    this.authorsVariantsNumber = this.data[1].authorsVariants.duplicates.length;
    this.authorsToBeReplaced = []
    this.authorsToReplace = []
    this.selectMode('reset');
  }

  updateOrganizationsVariantsList(organization:any, allowDuplicates:boolean = false) {
    let index = this.organizationsToBeReplaced.indexOf(organization.id);
    if (index >= 0 && !allowDuplicates) {
      this.organizationsToBeReplaced.splice(index,1);
      this.organizationsToReplace.splice(index,1);
    }
    else {
      index = this.primaryOrganizations.data.indexOf(organization);
      if (index >= 0) {
        this.organizationsToReplace.push(this.secondaryOrganizations.data[index].id);
      }
      else {
        index = this.secondaryOrganizations.data.indexOf(organization);
        this.organizationsToReplace.push(this.primaryOrganizations.data[index].id);
      }
      this.organizationsToBeReplaced.push(organization.id);
    }
  }

  clearOrganizationsDuplicates() {
    let filteredData = this.data[0];
    let replacingOrganizationsObjects = this.organizationsToReplace.map((organizationId:string) => filteredData.find((object:any) => object.organizationId === organizationId));

    for (let i = 0; i < filteredData.length; i++) {
      let index = this.organizationsToBeReplaced.indexOf(filteredData[i].organizationId);
      if (index >= 0) {
        filteredData[i].organizationId = replacingOrganizationsObjects[index].organizationId;
        filteredData[i].organizationName = replacingOrganizationsObjects[index].organizationName;
        filteredData[i].organizationType1 = replacingOrganizationsObjects[index].organizationType1;
        filteredData[i].organizationType2 = replacingOrganizationsObjects[index].organizationType2;
        filteredData[i].organizationCity = replacingOrganizationsObjects[index].organizationCity;
        filteredData[i].organizationCountry = replacingOrganizationsObjects[index].organizationCountry;
      }
    }

    this._searchService.setTableData(filteredData);
    for (let i = 0; i < this.organizationsToBeReplaced.length; i++) {
      let index = this.primaryOrganizations.data.indexOf(this.primaryOrganizations.data.find((x:any) => x.id === this.organizationsToBeReplaced[i])) > -1
      ? this.primaryOrganizations.data.indexOf(this.primaryOrganizations.data.find((x:any) => x.id === this.organizationsToBeReplaced[i]))
      : this.secondaryOrganizations.data.indexOf(this.secondaryOrganizations.data.find((x:any) => x.id === this.organizationsToBeReplaced[i]));

      this.primaryOrganizations.data.splice(index,1);
      this.secondaryOrganizations.data.splice(index,1);
    }

    this.organizationsVariantsNumber = this.data[1].organizationsVariants.duplicates.length;
    this.organizationsToBeReplaced = [];
    this.organizationsToReplace = [];
    this.selectMode('reset');
  }

}
