import pandas as pd
import json

publications_per_country = {}
countries_group = []

with open('JsonFiles\Records2003.json','r') as f:
    records = json.load(f)

publications_dois = []
for index in records.keys():
    if(records[index]['DOI'] not in publications_dois):
        publications_dois.append(records[index]['DOI'])

for i in range(1, len(records.keys())):
    if(records[str(i)]['DOI'] == records[str(i-1)]['DOI']):
        if(records[str(i)]['Country'] not in countries_group):
            countries_group.append(records[str(i)]['Country'])
    
        if(records[str(i-1)]['Country'] not in countries_group):
            countries_group.append(records[str(i-1)]['Country'])
    
    else:
        for country in countries_group:
            if(country not in publications_per_country.keys()):
                publications_per_country[country] = 1
            else:
                publications_per_country[country] += 1

        countries_group = []

for country in publications_per_country.keys():
    publications_per_country[country] = round(publications_per_country[country]/len(publications_dois)*100, 2)

countries_column = [country for country in publications_per_country.keys()]
publications_column = [publications_per_country[country] for country in publications_per_country.keys()]

df = pd.DataFrame({'Countries': countries_column, 'Publications': publications_column})
df.to_excel('ExcelFiles/PublicationsPerCountry2003.xlsx')