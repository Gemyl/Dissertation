from DbContext.Services import get_db_connection_and_cursor
import pandas as pd

countries = ['United States', 'United Kingdom', 'Japan',
             'Germany', 'China', 'Canada', 'France', 'India']
interactions = {}
total_interactions = {}

for country in countries:
    interactions[country] = {}
    total_interactions[country] = 0

connection, cursor = get_db_connection_and_cursor()

publications_ids = []
query = f'SELECT ID from scopus_publications WHERE Year = \'2000\' OR Year = \'2001\' OR Year = \'2002\' OR Year = \'2003\' OR Year = \'2004\';'
cursor.execute(query)
publications_ids = [pub[0] for pub in cursor.fetchall()]

for id in publications_ids:
    query = f'SELECT scopus_organizations.Country FROM \
            ((scopus_publications \
            INNER JOIN scopus_publications_organizations \
            ON scopus_publications.ID = scopus_publications_organizations.Publication_ID) \
            INNER JOIN scopus_organizations \
            ON scopus_publications_organizations.Organization_ID = scopus_organizations.ID) \
            WHERE scopus_publications.ID = \'{id}\';'

    cursor.execute(query)
    fetched_countries = cursor.fetchall()
    if (len(fetched_countries) > 1):
        countries_group = []
        for country in fetched_countries:
            if (country[0] not in countries_group):
                countries_group.append(country[0])

        countries_set = set(countries)
        countries_group_set = set(countries_group)

        countries_intersection = countries_set.intersection(
            countries_group_set)

        if (len(countries_intersection) > 1):
            for root_country in countries_intersection:
                for child_country in countries_intersection:
                    if (root_country != child_country):
                        if (child_country not in interactions[root_country].keys()):
                            interactions[root_country][child_country] = 1
                        else:
                            interactions[root_country][child_country] += 1

                        total_interactions[root_country] += 1

writer = pd.ExcelWriter('InteractionsPerCountry.xlsx', engine='xlsxwriter')

for root_country in interactions.keys():
    countries_column = []
    interactions_column = []

    for child_country in interactions[root_country].keys():
        countries_column.append(child_country)
        interactions_column.append(round(
            interactions[root_country][child_country]/total_interactions[root_country]*100, 2))

    df = pd.DataFrame({'Country': countries_column,
                      'Interactions Share': interactions_column})
    df.to_excel(writer, root_country, index=False)

writer.save()