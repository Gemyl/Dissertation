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
  public originalAuthors: any;
  public originalOrganizations: any;
  public duplicatesPublications: any;
  public duplicatesAuthors: any;
  public duplicatesOrganizations: any;
  public publicationsTableColumns = ["title", "citationsCount", "checkbox"]
  public authorsTableColumns = ["name", "citationsCount", "hIndex", "checkbox"]
  public organizationsTableColumns = ["name", "checkbox"]
  public publicationsToRemove: string[] = [];
  public authorsToBeReplaced: string[] = [];
  public authorsToReplace: string[] = [];
  public organizationsToBeReplaced: string[] = [];
  public organizationsToReplace: string[] = [];
  public dialogResult: boolean = true;

  constructor(
    public dialogRef: MatDialogRef<DuplicatesDetectionScreenComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private _searchService: SearchService
  ) { 
    this.originalPublications = new MatTableDataSource(this.data[1].publicationsVariants.originals);
    this.duplicatesPublications = new MatTableDataSource(this.data[1].publicationsVariants.duplicates);
    this.originalPublications.data = this.data[1].publicationsVariants.originals;
    this.duplicatesPublications.data = this.data[1].publicationsVariants.duplicates;

    this.originalAuthors = new MatTableDataSource(this.data[1].authorsVariants.originals);
    this.duplicatesAuthors = new MatTableDataSource(this.data[1].authorsVariants.duplicates);
    this.originalAuthors.data = this.data[1].authorsVariants.originals;
    this.duplicatesAuthors.data = this.data[1].authorsVariants.duplicates;

    this.originalOrganizations = new MatTableDataSource(this.data[1].organizationsVariants.originals);
    this.duplicatesOrganizations = new MatTableDataSource(this.data[1].organizationsVariants.duplicates);
    this.originalOrganizations.data = this.data[1].organizationsVariants.originals;
    this.duplicatesOrganizations.data = this.data[1].organizationsVariants.duplicates;
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

  updatePublicationsVariantsList(publicationId:string) {
    let index = this.publicationsToRemove.indexOf(publicationId);
    if (index >= 0) {
      this.publicationsToRemove.splice(index,1);
    }
    else {
      this.publicationsToRemove.push(publicationId);
    }
  }

  clearPublicationsDuplicates() {
    let filteredData = this.data[0];

    for(let i = 0; i < this.publicationsToRemove.length; i++) {
      let removedItem = this.data[1].publicationsVariants.duplicates.find((x:any) => x.id != this.publicationsToRemove[i]);
      let index = this.data[1].publicationsVariants.duplicates.indexOf(removedItem);
      this.data[1].publicationsVariants.originals.splice(index,1);
      this.data[1].publicationsVariants.duplicates.splice(index,1);
      filteredData = filteredData.filter((x:any) => x.publicationId != this.publicationsToRemove[i]); 
    }
    this._searchService.setTableData(filteredData);
    this.publicationsVariantsNumber = this.data[1].publicationsVariants.duplicates.length;
    this.selectMode('reset');
  }

  updateAuthorsVariantsList(author:any) {
    let index = this.authorsToBeReplaced.indexOf(author.id);
    if (index >= 0) {
      this.authorsToBeReplaced.splice(index,1);
      this.authorsToReplace.splice(index,1);
    }
    else {
      index = this.originalAuthors.data.indexOf(author);
      if (index >= 0) {
        this.authorsToReplace.push(this.duplicatesAuthors.data[index].id);
      }
      else {
        index = this.duplicatesAuthors.data.indexOf(author);
        this.authorsToReplace.push(this.originalAuthors.data[index].id);
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
      this.data[1].authorsVariants.originals.splice(i,1);
      this.data[1].authorsVariants.duplicates.splice(i,1);
    }

    this.authorsVariantsNumber = this.data[1].authorsVariants.duplicates.length;
    this.selectMode('reset');
  }

  updateOrganizationsVariantsList(organization:any) {
    let index = this.organizationsToBeReplaced.indexOf(organization.id);
    if (index >= 0) {
      this.organizationsToBeReplaced.splice(index,1);
      this.organizationsToReplace.splice(index,1);
    }
    else {
      index = this.originalOrganizations.data.indexOf(organization);
      if (index >= 0) {
        this.organizationsToReplace.push(this.duplicatesAuthors.data[index].id);
      }
      else {
        index = this.duplicatesOrganizations.data.indexOf(organization);
        this.organizationsToReplace.push(this.originalOrganizations.data[index].id);
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
      this.data[1].organizationsVariants.originals = this.data[1].organizationsVariants.originals.filter((x:any) => x.id != this.organizationsToReplace[i]);
      this.data[1].organizationsVariants.duplicates = this.data[1].organizationsVariants.duplicates.filter((x:any) => x.id != this.organizationsToBeReplaced[i]);
    }

    this.organizationsVariantsNumber = this.data[1].organizationsVariants.duplicates.length;
    this.selectMode('reset');
  }

}
