from pybliometrics.scopus import AbstractRetrieval
from fuzzywuzzy import fuzz
from getpass import getpass
import mysql.connector as connector

# Colors
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BLUE = "\033[1;34m"

# Reset color to default
RESET = "\033[0m"

def detectPublicationsDuplicates(connection, cursor):
    # lists for storing data fetched from database
    ids = []
    dois = []
    titles = []
    abstracts = []
    keywords = []
    fields = []
    citationsCount = []

    # lists concetrating remained and removed variants
    variants1Ids = []
    variants2Ids = []
    removedTitles = []
    remainingTitles =[]

    # Retrieving data from database
    query = "SELECT ID FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        ids.append(row[0])

    query = "SELECT DOI FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        dois.append(row[0])

    query = "SELECT Title FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        titles.append(row[0])

    query = "SELECT Abstract FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        abstracts.append(row[0])

    query = "SELECT Keywords FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        keywords.append(row[0])

    query = "SELECT Fields FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        fields.append(row[0])

    query = "SELECT Citations_Count FROM scopus_publications ORDER BY Title;"
    cursor.execute(query)
    for row in cursor:
        citationsCount.append(row[0])

    # Duplicates detection algorithm
    for i in range(len(ids)-1):
        for j in range(i+1, len(ids)):

            if((fuzz.ratio(titles[i], titles[j]) > 85) & (fuzz.ratio(abstracts[i], abstracts[j]) > 85) & 
            (fuzz.ratio(keywords[i], keywords[j]) > 85) & (fuzz.ratio(fields[i], fields[j]) > 85)):
                firstPublicationCitations = citationsCount[i]
                seconnectiondPublicationCitations = citationsCount[j]

                if ((firstPublicationCitations > seconnectiondPublicationCitations) & (ids[i] not in variants2Ids)):
                    variants1Ids.append(ids[i])
                    variants2Ids.append(ids[j])
                    removedTitles.append(titles[j])
                    remainingTitles.append(titles[i])

                elif (ids[j] not in variants2Ids):
                    variants1Ids.append(ids[j])
                    variants2Ids.append(ids[i])
                    removedTitles.append(titles[i])
                    remainingTitles.append(titles[j])
            else:
                break

    # Printing results
    if len(removedTitles) == 0:
        print(f"{BLUE}No duplicates detected.")
    else:
        for i in range(len(removedTitles)):
            print(f'------------------\n'
                f'{GREEN}Remained variant: {remainingTitles[i]}{RESET}.\n'
                f'{RED}Rejected variant: {removedTitles[i]}{RESET}.\n'
                f'------------------')
            
            try:
                query = f"INSERT INTO scopus_publications_variants VALUES ('{variants1Ids[i]}', '{variants2Ids[i]}');"
                cursor.execute(query)
                connection.commit()
            except:
                pass