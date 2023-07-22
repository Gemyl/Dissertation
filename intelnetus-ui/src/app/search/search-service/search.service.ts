import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from 'src/environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private apiUrl: string;
  private tableData$: BehaviorSubject<any> = new BehaviorSubject<any>([]);

  constructor(
    private httpClient: HttpClient
  ) { 
    this.apiUrl = environment.apiUrl;
  }

  getMetadata(keywords: any, booleans: any, year1: string, year2: string, fields: any, apiKey: string): Observable<any> {
    let params = new HttpParams()
      .set('keywords', keywords)
      .set('booleans', booleans)
      .set('year1', year1)
      .set('year2', year2)
      .set('fields', fields)
      .set('scopusApiKey', apiKey)

    return this.httpClient.get(this.apiUrl, {params: params});
  }

  getTableData(): Observable<any> {
    return this.tableData$.asObservable();
  }

  setTableData(data: Array<any>[]): void {
    this.tableData$.next(data);
  } 
}
