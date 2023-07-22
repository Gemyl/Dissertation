import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private apiUrl = "http://127.0.0.1:5000/search";
  private tableData$: BehaviorSubject<any> = new BehaviorSubject<any>([]);

  constructor(
    private httpClient: HttpClient
  ) { }

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
