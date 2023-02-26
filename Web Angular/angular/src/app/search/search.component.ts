import { Component} from '@angular/core';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent{

  onSubmit(event: Event) {
    const form = document.getElementById('search-form') as HTMLFormElement; 
    const formData = new FormData(form);

    const requestOptions: RequestInit = {
      method: 'POST',
      body: formData
    };

    fetch('http://localhost:5000/search', requestOptions)
    .then(reponse => reponse.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));

    form.reset();
    event.preventDefault();
  }
  
}