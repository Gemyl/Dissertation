import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SearchService {
  private tableData: BehaviorSubject<any> = new BehaviorSubject<any>([]);
  constructor() { }

  getTableData(): Observable<any> {
    return this.tableData.asObservable();
  }

  setTableData(data: Array<any>[]): void {
    this.tableData.next(data);
  } 
}
