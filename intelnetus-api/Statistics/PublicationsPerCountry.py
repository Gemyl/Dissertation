from DbContext.Services import get_db_connection_and_cursor
import pandas as pd

publications_per_country = {}
publications_per_country_percentage = {}
total_publications_per_year = {}
years_list = ['2004']

connection, cursor = get_db_connection_and_cursor()

for year in years_list:
    query = f'SELECT ID from scopus_publications WHERE Year = \'{year}\';'
    cursor.execute(query)
    publications_ids = [pub[0] for pub in cursor.fetchall()]
    total_publications_per_year[year] = len(publications_ids)

    for id in publications_ids:
        query = f'SELECT scopus_organizations.Country FROM \
                ((scopus_publications \
                INNER JOIN scopus_publications_organizations \
                ON scopus_publications.ID = scopus_publications_organizations.Publication_ID) \
                INNER JOIN scopus_organizations \
                ON scopus_publications_organizations.Organization_ID = scopus_organizations.ID) \
                WHERE scopus_publications.ID = \'{id}\';'
        
        cursor.execute(query)

        countries_group = []
        for country in cursor.fetchall():
            if (country[0] not in countries_group):
                countries_group.append(country[0])
            
                if (country[0] not in publications_per_country.keys()):
                    publications_per_country[country[0]] = {}
                    
                if (year not in publications_per_country[country[0]].keys()):
                    publications_per_country[country[0]][year] = 1
                else:
                    publications_per_country[country[0]][year] += 1

cursor.close()
connection.close()

for country in publications_per_country.keys():
    for year in publications_per_country[country].keys():
        publications_per_country[country][year] = round(publications_per_country[country][year]/total_publications_per_year[year]*100, 2)

writer = pd.ExcelWriter('PublicationsPerCountry2004.xlsx', 'xlsxwriter')

for year in years_list:
    countries_column = []
    publications_number_column = []

    for country in publications_per_country.keys():
        if year in publications_per_country[country].keys():
            countries_column.append(country)
            publications_number_column.append(publications_per_country[country][year])

    df = pd.DataFrame({'Country':countries_column, 'Publications Share':publications_number_column})
    df.to_excel(writer, sheet_name=f'{year}', index=False)
    
writer.save()